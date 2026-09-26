import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
FINAL = ROOT / "output" / "final_video.mp4"
JOBS = ROOT / "output" / "web_jobs"
JOBS.mkdir(parents=True, exist_ok=True)

# Import the existing AI pipeline functions. Importing main.py does not
# execute its CLI because its entrypoint is guarded by __main__.
import main as pipeline

app = FastAPI(title="FrameForge AI API")
jobs: dict[str, dict[str, Any]] = {}
script_jobs: dict[str, dict[str, Any]] = {}


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=1000)
    duration: int = Field(60, ge=5, le=1800)
    tone: str = "educational"
    audience: str = "general audience"
    provider: str = "local"
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    code_model: str = ""


class ScriptEditRequest(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=3000)


def validate_provider(request: GenerateRequest) -> None:
    provider = request.provider.strip().lower() or "local"
    if provider not in {"local", "xai", "openai", "gemini", "custom"}:
        raise HTTPException(400, f"Unsupported provider: {provider}.")
    if provider != "local" and not request.api_key.strip():
        raise HTTPException(400, f"API key is required for provider '{provider}'.")
    if provider == "custom" and (not request.model.strip() or not request.base_url.strip()):
        raise HTTPException(400, "Custom provider requires model and base URL.")


def make_state(request: GenerateRequest) -> dict[str, Any]:
    return {
        "topic": request.topic.strip(),
        "duration": int(request.duration),
        "tone": request.tone.strip() or "educational",
        "audience": request.audience.strip() or "general audience",
        "provider": request.provider.strip().lower() or "local",
        "api_key": request.api_key.strip(),
        "model": request.model.strip(),
        "base_url": request.base_url.strip(),
        "code_model": request.code_model.strip(),
    }


async def generate_script_task(jobid: str, request: GenerateRequest) -> None:
    job = script_jobs[jobid]
    try:
        job.update(status="running", progress=5, stage="Writing script...")
        job["logs"].append("Starting standalone script generation.")

        state = make_state(request)
        result = await asyncio.to_thread(pipeline.script_writer, state)
        script = result["script"]

        job["state"] = state
        job["script"] = script
        job.update(status="completed", progress=100, stage="Script ready for review.")
        job["logs"].append(f"Generated {len(script.scenes)} scenes totaling {script.total_duration}s.")
    except Exception as exc:
        job.update(status="failed", progress=100, stage="Script generation failed.", error=str(exc))
        job["logs"].append("ERROR: " + str(exc))


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/script")
async def create_script(request: GenerateRequest):
    if not request.topic.strip():
        raise HTTPException(400, "Topic cannot be empty.")
    validate_provider(request)

    if any(job["status"] == "running" for job in script_jobs.values()):
        raise HTTPException(409, "A script is already being generated. Wait for it to finish.")

    jobid = uuid.uuid4().hex[:10]
    script_jobs[jobid] = {
        "status": "running",
        "progress": 3,
        "stage": "Starting script agent...",
        "logs": [],
        "error": None,
        "script": None,
        "state": None,
        "approved": False,
    }
    asyncio.create_task(generate_script_task(jobid, request))
    return {"job_id": jobid, "status": "running"}


@app.get("/api/script/{jobid}")
async def script_status(jobid: str):
    job = script_jobs.get(jobid)
    if not job:
        raise HTTPException(404, "Script job not found.")

    payload = {
        "status": job["status"],
        "progress": job["progress"],
        "stage": job["stage"],
        "logs": job["logs"],
        "error": job["error"],
    }
    if job["script"] is not None:
        payload["script"] = job["script"].model_dump()
    return payload


@app.post("/api/script/{jobid}/edit")
async def edit_script(jobid: str, request: ScriptEditRequest):
    job = script_jobs.get(jobid)
    if not job or job["script"] is None:
        raise HTTPException(404, "Script not found.")
    if job["approved"]:
        raise HTTPException(409, "Approved scripts cannot be edited. Generate or edit before approval.")

    try:
        llm = pipeline.get_agent_llm(job["state"])
        edited = await asyncio.to_thread(
            pipeline.edit_video_script,
            job["script"],
            request.instruction.strip(),
            llm,
        )
        pipeline.validate_script(edited, expected_duration=job["state"]["duration"])
        job["script"] = edited
        job["logs"].append("Script edited successfully.")
        return {"status": "completed", "script": edited.model_dump()}
    except Exception as exc:
        raise HTTPException(400, f"Script edit failed: {exc}") from exc


@app.post("/api/script/{jobid}/regenerate")
async def regenerate_script(jobid: str):
    job = script_jobs.get(jobid)
    if not job or job["state"] is None:
        raise HTTPException(404, "Script job not found.")
    if job["approved"]:
        raise HTTPException(409, "Approved scripts cannot be regenerated.")

    try:
        regenerated = await asyncio.to_thread(pipeline.regenerate_script, job["state"])
        pipeline.validate_script(regenerated, expected_duration=job["state"]["duration"])
        job["script"] = regenerated
        job["status"] = "completed"
        job["stage"] = "New script ready for review."
        job["logs"].append("Script regenerated successfully.")
        return {"status": "completed", "script": regenerated.model_dump()}
    except Exception as exc:
        raise HTTPException(400, f"Script regeneration failed: {exc}") from exc


@app.post("/api/script/{jobid}/cancel")
async def cancel_script(jobid: str):
    job = script_jobs.get(jobid)
    if not job:
        raise HTTPException(404, "Script job not found.")
    job["status"] = "cancelled"
    job["stage"] = "Script generation cancelled."
    job["logs"].append("Script workflow cancelled by user.")
    return {"status": "cancelled"}


@app.post("/api/script/{jobid}/approve")
async def approve_script(jobid: str):
    job = script_jobs.get(jobid)
    if not job or job["script"] is None:
        raise HTTPException(404, "Script not found.")
    if job["status"] != "completed":
        raise HTTPException(409, "Script is not ready for approval.")

    pipeline.validate_script(job["script"], expected_duration=job["state"]["duration"])
    job["approved"] = True
    job["logs"].append("Script approved by user.")
    return {"status": "approved", "script": job["script"].model_dump()}


@app.post("/api/script/{jobid}/save")
async def save_script(jobid: str):
    job = script_jobs.get(jobid)
    if not job or job["script"] is None:
        raise HTTPException(404, "Script not found.")
    if not job["approved"]:
        raise HTTPException(409, "Approve the script before saving it.")

    await asyncio.to_thread(pipeline.save_video_script, job["script"])
    job["logs"].append("Approved script saved to output/scripts/.")
    return {
        "status": "saved",
        "path": "output/scripts/approved_script.json",
        "text_path": "output/scripts/approved_script.txt",
    }


@app.post("/api/script/{jobid}/video")
async def generate_video_from_script(jobid: str):
    # The script-first UI is implemented first. The downstream video phase
    # will be wired to the approved script after this frontend test pass.
    job = script_jobs.get(jobid)
    if not job or job["script"] is None:
        raise HTTPException(404, "Script not found.")
    if not job["approved"]:
        raise HTTPException(409, "Approve the script before generating video.")
    raise HTTPException(501, "Video generation is intentionally not connected yet. Script-first frontend test is ready.")


# ---------------------------------------------------------------------------
# Legacy video endpoint retained for the old one-shot frontend/API clients.
# ---------------------------------------------------------------------------

def detect(line: str):
    x = line.lower()
    stages = [
        (("story writer", "writing story"), 8, "Writing story..."),
        (("scene planner", "planning scenes"), 18, "Planning scenes..."),
        (("asset planner", "asset plan"), 28, "Planning assets..."),
        (("image requirement", "image requirements"), 34, "Planning image requirements..."),
        (("code generator", "generating scene code"), 50, "Generating scene code..."),
        (("validator", "code validator", "validating"), 65, "Validating scene code..."),
        (("fixer", "code fixer", "fixing"), 70, "Fixing scene code..."),
        (("browser renderer", "browser", "playwright", "rendering"), 84, "Rendering browser frames..."),
        (("ffmpeg", "composing final mp4", "final video"), 96, "Composing final MP4..."),
    ]
    for words, progress, text in stages:
        if any(word in x for word in words):
            return progress, text
    return None


def clean_previous_outputs():
    for folder in (ROOT / "output" / "frames", ROOT / "output" / "generated_scenes"):
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True, exist_ok=True)
    if FINAL.exists():
        try:
            FINAL.unlink()
        except OSError:
            pass


async def run(jobid, request):
    job = jobs[jobid]
    process = None
    provider = request.provider.strip().lower() or "local"

    try:
        clean_previous_outputs()
        env = os.environ.copy()
        env["FRAMEFORGE_PROVIDER"] = provider
        env["FRAMEFORGE_API_KEY"] = request.api_key.strip()
        env["FRAMEFORGE_MODEL"] = request.model.strip()
        env["FRAMEFORGE_BASE_URL"] = request.base_url.strip()
        env["FRAMEFORGE_CODE_MODEL"] = request.code_model.strip()

        process = await asyncio.create_subprocess_exec(
            os.sys.executable, "-u", "main.py",
            cwd=str(ROOT), env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        inputs = "\n".join([
            request.topic.strip(),
            str(request.duration),
            request.tone.strip() or "educational",
            request.audience.strip() or "general audience",
        ]) + "\n"
        process.stdin.write(inputs.encode("utf-8"))
        await process.stdin.drain()
        process.stdin.close()

        while True:
            raw = await process.stdout.readline()
            if not raw:
                break
            line = raw.decode(errors="replace").rstrip()
            if line:
                job["logs"].append(line)
                detected = detect(line)
                if detected:
                    job["progress"], job["stage"] = detected

        rc = await process.wait()
        if rc != 0:
            raise RuntimeError(f"AI pipeline exited with code {rc}.")
        if not FINAL.exists():
            raise FileNotFoundError("output/final_video.mp4 was not created.")

        destination = JOBS / f"{jobid}.mp4"
        shutil.copy2(FINAL, destination)
        job.update(status="completed", progress=100, stage="Video complete.", video=str(destination))
    except Exception as exc:
        job.update(status="failed", error=str(exc))
        job["logs"].append("ERROR: " + str(exc))
    finally:
        if process and process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    validate_provider(request)
    if any(job["status"] == "running" for job in jobs.values()):
        raise HTTPException(409, "A video is already being generated. Wait for it to finish.")

    jobid = uuid.uuid4().hex[:10]
    jobs[jobid] = {
        "status": "running",
        "progress": 3,
        "stage": "Starting AI agent...",
        "logs": [],
        "error": None,
        "video": None,
    }
    asyncio.create_task(run(jobid, request))
    return {"job_id": jobid, "status": "running"}


@app.get("/api/jobs/{jobid}")
async def status(jobid: str):
    if jobid not in jobs:
        raise HTTPException(404, "Job not found.")
    job = jobs[jobid]
    return {key: job[key] for key in ("status", "progress", "stage", "logs", "error")}


@app.get("/api/jobs/{jobid}/video")
async def video(jobid: str):
    job = jobs.get(jobid)
    if not job or job["status"] != "completed":
        raise HTTPException(404, "Video is not ready.")
    path = Path(job["video"])
    if not path.exists():
        raise HTTPException(404, "Video file not found.")
    return FileResponse(path, media_type="video/mp4", filename="frameforge-video.mp4")


app.mount("/", StaticFiles(directory=WEB, html=True), name="frontend")
