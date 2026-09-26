# FrameForge AI Video Agent

FrameForge is an AI-powered short-video generator that creates informational/reel-style videos using HTML, CSS, JavaScript, Playwright/Chromium, and FFmpeg.

The project is designed so that the AI writes the scene HTML/CSS/JS instead of relying on a fixed set of predefined video templates.

---

## 1. What the Project Does

The main flow is:

```text
USER
  ↓
SCRIPT WRITER
  ↓
SCRIPT PREVIEW
  ↓
USER APPROVAL
  ↓
DO YOU WANT VIDEO?
  ├── NO → SAVE SCRIPT → STOP
  └── YES
       ↓
SCENE PLANNER
       ↓
ASSET PLANNER
       ↓
IMAGE REQUIREMENT AGENT
       ↓
ASSET VERIFIER
       ↓
VISUAL / CODE GENERATOR
       ↓
HTML + CSS + JS
       ↓
CODE VALIDATOR
       ↓
CODE FIXER
       ↓
PLAYWRIGHT / CHROMIUM
       ↓
FRAMES
       ↓
FFMPEG
       ↓
FINAL MP4
       ↓
VIDEO VERIFICATION
```

---

# 2. Requirements

For a fresh Windows installation, you should have:

- Windows 10/11
- Python 3.10
- Ollama
- Qwen3 8B model
- FFmpeg + FFprobe
- Node.js + npm
- Chromium for Playwright
- Git (optional but recommended)

> **Important:** `pip` installs Python packages only. It does NOT install Ollama, FFmpeg, Node.js, or the Chromium browser binary.

---

# 3. Check What Is Already Installed

Open PowerShell and run:

```powershell
python --version
```

Recommended:

```text
Python 3.10.x
```

Check Node.js:

```powershell
node --version
npm --version
```

Check Ollama:

```powershell
ollama --version
```

Check FFmpeg:

```powershell
ffmpeg -version
```

Check FFprobe:

```powershell
ffprobe -version
```

If a command is not recognized, install the missing dependency using the sections below.

---

# 4. Install Python 3.10

The project is tested with Python 3.10.

Check:

```powershell
python --version
```

If Python 3.10 is not installed, install Python 3.10 from the official Python installer.

After installation, verify:

```powershell
py -3.10 --version
```

Example:

```text
Python 3.10.10
```

If multiple Python versions are installed, create the virtual environment specifically with Python 3.10:

```powershell
py -3.10 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 5. Install Python Dependencies

First activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the main packages:

```powershell
python -m pip install -U langchain langgraph langchain-ollama playwright
```

If you want OpenAI/xAI provider support:

```powershell
python -m pip install -U langchain-openai
```

If you want Google Gemini provider support:

```powershell
python -m pip install -U langchain-google-genai
```

You can install both optional provider packages:

```powershell
python -m pip install -U langchain-openai langchain-google-genai
```

---

# 6. Install Ollama

Ollama is a separate application. It is NOT installed with pip.

Install Ollama using the official Ollama Windows installer.

After installation, close and reopen PowerShell.

Verify:

```powershell
ollama --version
```

Then check installed models:

```powershell
ollama list
```

---

# 7. Install Qwen3 8B

FrameForge currently uses Qwen3 8B as the default local model.

Pull it with:

```powershell
ollama pull qwen3:8b
```

Verify:

```powershell
ollama list
```

You should see something similar to:

```text
qwen3:8b
```

Test the model:

```powershell
ollama run qwen3:8b
```

Type:

```text
Explain what a solar eclipse is in simple English.
```

Press `Ctrl+D` or exit the Ollama session when finished.

---

# 8. Ollama Environment Variable

FrameForge can use:

```text
http://127.0.0.1:11434
```

If Ollama is not reachable correctly, set the Windows user environment variable:

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "http://127.0.0.1:11434", "User")
```

Then close and reopen PowerShell.

Check:

```powershell
$env:OLLAMA_HOST
```

Expected:

```text
http://127.0.0.1:11434
```

You can also verify Ollama directly:

```powershell
curl http://localhost:11434
```

---

# 9. Install FFmpeg + FFprobe

FFmpeg is required to convert the captured frames into the final MP4 video.

FFprobe is used to inspect and verify the generated MP4.

## Option A — Install with winget

On Windows, the easiest method is:

```powershell
winget install Gyan.FFmpeg
```

After installation, close and reopen PowerShell.

Verify:

```powershell
ffmpeg -version
```

and:

```powershell
ffprobe -version
```

Both commands should work.

---

## Option B — Install with Chocolatey

If Chocolatey is already installed:

```powershell
choco install ffmpeg -y
```

Then close and reopen PowerShell.

Verify:

```powershell
ffmpeg -version
```

```powershell
ffprobe -version
```

---

## Option C — Manual FFmpeg Installation

If `winget` or Chocolatey is not available:

1. Download a Windows FFmpeg build from a trusted FFmpeg distribution.
2. Extract the FFmpeg folder.
3. Locate the folder containing:
   - `ffmpeg.exe`
   - `ffprobe.exe`
4. Add that `bin` folder to the Windows `PATH`.
5. Close and reopen PowerShell.

Then verify:

```powershell
ffmpeg -version
```

```powershell
ffprobe -version
```

---

# 10. Install Node.js and npm

Node.js is required for the browser/rendering side of the project.

Check:

```powershell
node --version
npm --version
```

If Node.js is missing, install the current **Node.js LTS** Windows installer.

After installation, close and reopen PowerShell.

Verify:

```powershell
node --version
```

```powershell
npm --version
```

---

# 11. Install Node Project Dependencies

Go to the project directory.

Example:

```powershell
cd "C:\Users\aryan\Desktop\ai-video-agent (2)\ai-video-agent"
```

If `package.json` does not exist:

```powershell
npm init -y
```

Install Playwright:

```powershell
npm install playwright
```

If `package.json` already exists, normally just run:

```powershell
npm install
```

---

# 12. Install Chromium for Playwright

Installing the Python or Node Playwright package does not always mean the browser binary is installed.

For Python Playwright:

```powershell
python -m playwright install chromium
```

For Node Playwright:

```powershell
npx playwright install chromium
```

If you are unsure, running both is acceptable:

```powershell
python -m playwright install chromium
npx playwright install chromium
```

---

# 13. Verify Playwright

For Python:

```powershell
python -c "import playwright; print('Python Playwright OK')"
```

For Node:

```powershell
node -e "console.log(require('playwright') ? 'Node Playwright OK' : 'Playwright missing')"
```

---

# 14. Verify FFmpeg and Browser Before Running

Run:

```powershell
python --version
```

```powershell
ollama --version
```

```powershell
ffmpeg -version
```

```powershell
ffprobe -version
```

```powershell
node --version
```

```powershell
npm --version
```

Then:

```powershell
python -m playwright install chromium
```

Finally:

```powershell
ollama list
```

Make sure:

```text
qwen3:8b
```

is available.

---

# 15. Recommended Fresh Windows Setup

If you are setting up FrameForge on a completely new Windows machine, follow this order:

## Step 1 — Install Python 3.10

Verify:

```powershell
py -3.10 --version
```

## Step 2 — Install Node.js LTS

Verify:

```powershell
node --version
npm --version
```

## Step 3 — Install Ollama

Verify:

```powershell
ollama --version
```

## Step 4 — Install Qwen3 8B

```powershell
ollama pull qwen3:8b
```

## Step 5 — Install FFmpeg

Preferred:

```powershell
winget install Gyan.FFmpeg
```

Verify:

```powershell
ffmpeg -version
ffprobe -version
```

## Step 6 — Open the project

```powershell
cd "C:\Users\aryan\Desktop\ai-video-agent (2)\ai-video-agent"
```

## Step 7 — Create virtual environment

```powershell
py -3.10 -m venv .venv
```

## Step 8 — Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## Step 9 — Install Python packages

```powershell
python -m pip install --upgrade pip
python -m pip install -U langchain langgraph langchain-ollama playwright
```

Optional providers:

```powershell
python -m pip install -U langchain-openai langchain-google-genai
```

## Step 10 — Install Chromium

```powershell
python -m playwright install chromium
```

## Step 11 — Install Node dependencies

```powershell
npm install
```

If Playwright is missing:

```powershell
npm install playwright
```

Then:

```powershell
npx playwright install chromium
```

---

# 16. Start the Web Application

Open PowerShell in the project directory.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the backend:

```powershell
cd web
python backend/server.py
```

The server should normally start at:

```text
http://127.0.0.1:8000
```

Open that address in your browser.

---

# 17. Using the Frontend

The frontend follows a script-first workflow.

## Step 1 — Enter Topic

Example:

```text
A brother explains dengue to his younger sister
```

## Step 2 — Select Duration

Example:

```text
60
```

The AI decides the number of scenes and distributes the requested duration across them.

## Step 3 — Select Tone

Example:

```text
Educational
```

## Step 4 — Select Audience

Example:

```text
Children under 18
```

## Step 5 — Select Provider

For local Ollama:

```text
Local Ollama
```

## Step 6 — Model

You can explicitly enter:

```text
qwen3:8b
```

If the model field is empty, the local provider uses its configured default model.

## Step 7 — Generate Script

The system generates the script first.

You should review:

- Title
- Hook
- Tone
- Audience
- Scene count
- Scene duration
- Narration
- Dialogue
- Visual direction
- On-screen text
- CTA

The script is a standalone deliverable.

---

# 18. Script Approval

After the script is generated, review it.

The intended flow is:

```text
Generate Script
      ↓
Preview Script
      ↓
Edit / Regenerate if required
      ↓
Approve Script
      ↓
Ask: Do you want video?
```

If you choose:

```text
NO
```

the script is saved and the video pipeline stops.

The system should NOT run:

- Scene Planner
- Asset Planner
- Image Requirement Agent
- Code Generator
- Playwright
- FFmpeg

If you choose:

```text
YES
```

the video pipeline continues.

---

# 19. Video Generation Pipeline

After the user approves the script and requests a video:

```text
Approved Script
      ↓
Scene Planner
      ↓
Asset Planner
      ↓
Image Requirement Agent
      ↓
Asset Verification
      ↓
HTML/CSS/JS Code Generation
      ↓
Code Validation
      ↓
Code Fixing
      ↓
Playwright
      ↓
Frame Capture
      ↓
FFmpeg
      ↓
MP4
      ↓
Video Verification
```

---

# 20. Important Rendering Rules

The generated scene code is intended to be:

- 1080 × 1920
- 9:16 vertical format
- Offline/self-contained
- HTML + CSS + optional JavaScript
- Suitable for Playwright frame capture

The generated scene should not depend on:

- External CDNs
- External API requests
- `fetch`
- `axios`
- `XMLHttpRequest`
- WebSocket
- React
- Tailwind CDN
- Video generation APIs

CSS animations and JavaScript-based animation are allowed.

---

# 21. Output Folders

Generated files are stored under the project's output directory.

Typical folders include:

```text
output/
├── scripts/
├── generated_scenes/
├── frames/
├── videos/
└── render_reports/
```

The exact contents can change depending on the current pipeline implementation.

---

# 22. Common Errors

## Error: Python is not recognized

Check:

```powershell
python --version
```

If missing, install Python and make sure it is available in PATH.

You can also use:

```powershell
py -3.10 --version
```

---

## Error: `No module named langgraph`

Run inside the activated virtual environment:

```powershell
python -m pip install -U langgraph
```

---

## Error: `No module named langchain_ollama`

Run:

```powershell
python -m pip install -U langchain-ollama
```

---

## Error: `No module named playwright`

Run:

```powershell
python -m pip install -U playwright
```

Then:

```powershell
python -m playwright install chromium
```

---

## Error: `playwright` browser executable missing

Run:

```powershell
python -m playwright install chromium
```

---

## Error: `npm` is not recognized

Install Node.js LTS and reopen PowerShell.

Check:

```powershell
node --version
npm --version
```

---

## Error: `ffmpeg` is not recognized

Install FFmpeg.

Preferred:

```powershell
winget install Gyan.FFmpeg
```

Then close and reopen PowerShell.

Verify:

```powershell
ffmpeg -version
```

---

## Error: `ffprobe` is not recognized

FFprobe normally comes with FFmpeg.

Verify:

```powershell
ffprobe -version
```

If it is missing, reinstall a complete FFmpeg build and ensure its `bin` directory is in PATH.

---

## Error: Ollama is not recognized

Install Ollama, then reopen PowerShell.

Verify:

```powershell
ollama --version
```

---

## Error: Qwen model not found

Run:

```powershell
ollama pull qwen3:8b
```

Then:

```powershell
ollama list
```

---

## Error: Ollama connection failed

Check:

```powershell
curl http://localhost:11434
```

If required, set:

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "http://127.0.0.1:11434", "User")
```

Then restart PowerShell.

---

# 23. Dependency Installation Summary

### Python

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -U langchain langgraph langchain-ollama playwright
python -m playwright install chromium
```

### Optional LLM Providers

```powershell
python -m pip install -U langchain-openai langchain-google-genai
```

### Ollama

```powershell
ollama pull qwen3:8b
ollama list
```

### Node.js

Install Node.js LTS, then:

```powershell
npm install
```

If Playwright is not installed:

```powershell
npm install playwright
npx playwright install chromium
```

### FFmpeg

```powershell
winget install Gyan.FFmpeg
```

Verify:

```powershell
ffmpeg -version
ffprobe -version
```

---

# 24. Quick Health Check

Run the following commands one by one:

```powershell
python --version
```

```powershell
node --version
```

```powershell
npm --version
```

```powershell
ollama --version
```

```powershell
ollama list
```

```powershell
ffmpeg -version
```

```powershell
ffprobe -version
```

```powershell
python -c "import langgraph; print('LangGraph OK')"
```

```powershell
python -c "import langchain_ollama; print('LangChain Ollama OK')"
```

```powershell
python -c "import playwright; print('Python Playwright OK')"
```

If all checks work, the machine is ready for the FrameForge pipeline.

---

# 25. Recommended First Test

Before generating a long video, use a short test.

Example:

```text
Topic:
Why do we need to drink water?

Duration:
30 seconds

Tone:
Educational

Audience:
General audience
```

Use:

```text
Provider: Local Ollama
Model: qwen3:8b
```

First test the script.

Then approve it.

Then choose video generation.

This makes debugging easier because a 30-second video produces fewer frames and completes faster than a 180-second video.

---

# 26. Debugging Order

If something fails, check dependencies in this order:

```text
1. Python
2. Virtual Environment
3. Python Packages
4. Ollama
5. Qwen3 8B
6. Node.js
7. npm dependencies
8. Playwright
9. Chromium
10. FFmpeg
11. FFprobe
12. Backend
13. Frontend
14. Video Pipeline
```

Do not reinstall the entire project immediately. First identify which layer is failing.

---

# 27. Important Note About AI Quality

The local Qwen3 8B model can generate the script, but AI-generated content should still be validated.

For production-quality scripts, the pipeline should validate:

- Correct scene duration
- Sequential scene IDs
- Missing fields
- Repeated sentences
- Semantic repetition
- Language quality
- Audience suitability
- Scene-to-scene flow
- Factual correctness
- Dialogue quality
- CTA quality

A script that passes structural validation is not automatically factually correct.

---

# 28. Project Philosophy

FrameForge is intended to be an agent-driven system rather than a collection of fixed video templates.

The LLM should be able to decide:

- How many scenes are required
- Where scene boundaries should occur
- What each scene should communicate
- Whether a visual asset is required
- What HTML/CSS/JS should be generated
- How the scene should animate

The deterministic parts of the system should focus on:

- Validation
- File management
- Browser rendering
- Frame capture
- FFmpeg encoding
- Video verification
- Error handling
- Retry limits

This separation makes the system easier to extend and debug.
