# FrameForge AI --- First-Time User Guide

## What is FrameForge AI?

FrameForge AI turns an idea into a short-form video through an AI
pipeline.

Main flow:

`Idea → Script → Review → Approval → Video Decision → Scene Planning → HTML/CSS/JS → Playwright → FFmpeg → MP4`

The application is **script-first**. The video pipeline must not start
until the user approves the script and explicitly chooses to generate a
video.

------------------------------------------------------------------------

## 1. Requirements

Recommended:

-   Python 3.10.x
-   Ollama
-   FFmpeg
-   Node.js/npm
-   Windows PowerShell

Check Python:

``` powershell
python --version
where.exe python
py -0p
```

Use Python 3.10.x for this project.

------------------------------------------------------------------------

## 2. First-Time Python Setup

Open PowerShell in the project root.

``` powershell
cd "C:\path oi-video-agent"
```

Create the virtual environment:

``` powershell
py -3.10 -m venv .venv
```

Activate it:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Install core dependencies:

``` powershell
python -m pip install --upgrade pip
python -m pip install -U langchain langgraph langchain-ollama playwright
```

If API providers are used:

``` powershell
python -m pip install -U langchain-openai langchain-google-genai
```

Install Chromium:

``` powershell
python -m playwright install chromium
```

Verify:

``` powershell
python -c "from langchain_ollama import ChatOllama; print('Ollama integration OK')"
python -c "import langgraph; print('LangGraph OK')"
python -c "from playwright.async_api import async_playwright; print('Playwright OK')"
```

------------------------------------------------------------------------

## 3. Ollama Setup

Check Ollama:

``` powershell
ollama --version
```

Check installed models:

``` powershell
ollama list
```

For the current local setup, the preferred model is:

``` text
qwen3:8b
```

If it is missing:

``` powershell
ollama pull qwen3:8b
```

Test it:

``` powershell
ollama run qwen3:8b
```

The frontend can explicitly use:

``` text
Local Ollama
Model: qwen3:8b
```

If the Model field is empty, the local provider currently falls back to
`qwen3:8b`.

------------------------------------------------------------------------

## 4. FFmpeg

Check:

``` powershell
ffmpeg -version
ffprobe -version
```

Both commands must work before testing final MP4 rendering.

If Windows says `ffmpeg` is not recognized, install FFmpeg and add its
`bin` directory to PATH.

------------------------------------------------------------------------

## 5. Start the Web Application

Activate `.venv`, then run:

``` powershell
python -m uvicorn web.backend.server:app --host 127.0.0.1 --port 8000
```

Successful startup:

``` text
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Open:

``` text
http://127.0.0.1:8000
```

Keep the terminal running while using the website.

Stop the server:

``` text
Ctrl+C
```

------------------------------------------------------------------------

## 6. First-Time Web Usage

### Step 1 --- Enter a topic

Example:

``` text
Explain how a solar eclipse happens to a general audience.
The video should explain the alignment of the Sun, Moon, and Earth,
why the Moon can block the Sun from our view, and the difference
between a total and partial solar eclipse.
Use simple English and avoid overly technical terminology.
```

### Step 2 --- Set duration

Example:

``` text
60
```

### Step 3 --- Set tone

``` text
educational
```

### Step 4 --- Set audience/language

``` text
General audience, simple English
```

### Step 5 --- Select provider

``` text
Local Ollama
```

### Step 6 --- Select model

``` text
qwen3:8b
```

### Step 7 --- Click

``` text
Generate Script
```

Do not expect the video to start immediately.

------------------------------------------------------------------------

## 7. Script Review

The application first shows:

-   Title
-   Duration
-   Tone
-   Audience
-   Hook
-   Scene durations
-   Narration
-   Visual direction
-   On-screen text
-   CTA

Actions:

``` text
Edit Script
Regenerate
Approve Script
Cancel
```

### Edit Script

Use this when the script is mostly correct but specific content should
change.

### Regenerate

Use this when you want a new script.

### Approve Script

Approves the script as the source of truth for downstream video
generation.

### Cancel

Stops the workflow.

**Cancel must not save the script as an approved script and must not
start video generation.**

------------------------------------------------------------------------

## 8. Video Confirmation

After script approval, the application should separately ask:

``` text
Do you want to generate the video?
```

Expected behavior:

``` text
YES → Video pipeline starts
NO  → Save approved script → Stop
```

If the user selects **NO**, these stages must not run:

-   Scene Planner
-   Asset Planner
-   Image Requirement Agent
-   HTML/CSS/JS Code Generator
-   Playwright
-   FFmpeg

------------------------------------------------------------------------

## 9. Main Pipeline

``` text
USER
 ↓
SCRIPT WRITER
 ↓
SCRIPT PREVIEW
 ↓
USER APPROVAL
 ├── CANCEL → STOP
 └── APPROVE
       ↓
DO YOU WANT VIDEO?
 ├── NO → SAVE SCRIPT → STOP
 └── YES
       ↓
SCENE / STYLE PLANNER
       ↓
ASSET PLANNER
       ↓
IMAGE REQUIREMENT AGENT
       ↓
ASSET VERIFIER
       ↓
HTML/CSS/JS CODE GENERATOR
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
VERIFICATION
```

------------------------------------------------------------------------

## 10. Important Commands

### Activate environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

### Python version

``` powershell
python --version
```

### Python location

``` powershell
where.exe python
```

### Ollama models

``` powershell
ollama list
```

### Run Qwen

``` powershell
ollama run qwen3:8b
```

### Install Ollama integration

``` powershell
python -m pip install -U langchain-ollama
```

### Install LangGraph

``` powershell
python -m pip install -U langgraph
```

### Install Playwright

``` powershell
python -m pip install -U playwright
```

### Install Chromium

``` powershell
python -m playwright install chromium
```

### FFmpeg check

``` powershell
ffmpeg -version
```

### FFprobe check

``` powershell
ffprobe -version
```

### Start web server

``` powershell
python -m uvicorn web.backend.server:app --host 127.0.0.1 --port 8000
```

### Open web app

``` text
http://127.0.0.1:8000
```

### Run CLI pipeline

``` powershell
python main.py
```

------------------------------------------------------------------------

## 11. Common Errors

### `No module named 'langchain_ollama'`

``` powershell
python -m pip install -U langchain-ollama
```

### `No module named 'langgraph'`

``` powershell
python -m pip install -U langgraph
```

### `No module named 'playwright'`

``` powershell
python -m pip install -U playwright
python -m playwright install chromium
```

### `ffmpeg is not recognized`

Install FFmpeg and add its `bin` folder to PATH.

### Ollama model not found

``` powershell
ollama list
ollama pull qwen3:8b
```

### Frontend appears unchanged

Hard refresh:

``` text
Ctrl + Shift + R
```

------------------------------------------------------------------------

## 12. Recommended First Test

Use:

``` text
Topic:
Explain how a solar eclipse happens to a general audience.
The video should explain the alignment of the Sun, Moon, and Earth,
why the Moon can block the Sun from our view, and the difference
between a total and partial solar eclipse.
Use simple English and avoid overly technical terminology.

Duration:
60

Tone:
educational

Audience:
General audience, simple English

Provider:
Local Ollama

Model:
qwen3:8b
```

First test only the script stage:

``` text
Generate Script
↓
Review Script
```

Do not start the full rendering pipeline until the script stage is
working correctly.

------------------------------------------------------------------------

## 13. Debugging Order

Always test in this order:

``` text
1. Python environment
2. Ollama
3. LLM model
4. FastAPI server
5. Frontend
6. Script generation
7. Script editing/regeneration
8. Script approval
9. Video confirmation
10. Scene planning
11. Asset planning
12. HTML/CSS/JS generation
13. Code validation
14. Playwright
15. FFmpeg
16. Final video verification
```

If an earlier stage fails, fix it before testing later stages.

------------------------------------------------------------------------

## 14. Important Development Rule

The approved script is the source of truth for the video.

Downstream visual agents should not rewrite:

-   Narration
-   Dialogue
-   Scene IDs
-   Scene durations
-   Approved spoken content

They should decide how the approved content is represented visually.

------------------------------------------------------------------------

## 15. Content Review

AI-generated content should be reviewed before publishing, especially
for:

-   Health
-   Safety
-   Scientific information
-   Legal information
-   Financial information
-   Other high-impact topics

The generated script should not automatically be treated as
authoritative.

------------------------------------------------------------------------

## Quick Start

For an already configured machine:

``` powershell
cd "C:\path oi-video-agent"
.\.venv\Scripts\Activate.ps1
ollama list
python -m uvicorn web.backend.server:app --host 127.0.0.1 --port 8000
```

Open:

``` text
http://127.0.0.1:8000
```

Select:

``` text
Local Ollama
qwen3:8b
```

Enter a topic and click:

``` text
Generate Script
```

Review the script before starting video generation.
