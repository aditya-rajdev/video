from pathlib import Path


# =========================================================
# RESPONSE TEXT EXTRACTOR
# =========================================================

def extract_text_from_response(response):
    """
    Extract text safely from LangChain AIMessage responses.

    Some providers return:

        response.content -> str

    Other providers may return:

        response.content -> list[dict | str]
    """

    content = response.content

    # -----------------------------------------------------
    # Normal string response
    # -----------------------------------------------------

    if isinstance(content, str):
        return content.strip()

    # -----------------------------------------------------
    # Structured/list response
    # -----------------------------------------------------

    if isinstance(content, list):

        parts = []

        for block in content:

            # Example:
            # "<html>...</html>"

            if isinstance(block, str):
                parts.append(block)

            # Example:
            # {"type": "text", "text": "<html>...</html>"}

            elif isinstance(block, dict):

                text = block.get("text")

                if isinstance(text, str):
                    parts.append(text)

        return "\n".join(parts).strip()

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return str(content).strip()


# =========================================================
# CLEAN GENERATED HTML
# =========================================================

def clean_generated_code(code):
    """
    Remove accidental Markdown code fences and text
    surrounding the generated HTML document.
    """

    if not isinstance(code, str):
        code = str(code)

    code = code.strip()

    # -----------------------------------------------------
    # Remove opening markdown fence
    # -----------------------------------------------------

    if code.lower().startswith("```html"):

        code = code[7:].strip()

    elif code.startswith("```"):

        code = code[3:].strip()

    # -----------------------------------------------------
    # Remove closing markdown fence
    # -----------------------------------------------------

    if code.endswith("```"):

        code = code[:-3].strip()

    # -----------------------------------------------------
    # Remove accidental text before <!DOCTYPE html>
    # -----------------------------------------------------

    doctype_index = code.lower().find(
        "<!doctype html>"
    )

    if doctype_index != -1:

        code = code[doctype_index:]

    else:

        # -------------------------------------------------
        # Fallback: find <html>
        # -------------------------------------------------

        html_index = code.lower().find(
            "<html"
        )

        if html_index != -1:

            code = code[html_index:]

    # -----------------------------------------------------
    # Remove accidental text after </html>
    # -----------------------------------------------------

    html_end_index = code.lower().rfind(
        "</html>"
    )

    if html_end_index != -1:

        code = code[
            :html_end_index + len("</html>")
        ]

    return code.strip()


# =========================================================
# GENERATE ONE SCENE
# =========================================================

def generate_scene_code(scene, llm):
    """
    Generate the complete HTML/CSS/JavaScript code
    for one video scene using the LLM supplied by main.py.

    The LLM can be:

        - Local Ollama
        - Gemini
        - OpenAI
        - xAI
        - Custom OpenAI-compatible provider

    This function does NOT hard-code any provider.
    """

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
You are an expert HTML5, CSS3 and JavaScript motion-graphics
video developer.

Your job is to generate the COMPLETE code for ONE video scene.

The scene will be rendered inside a Chromium browser and later
captured frame-by-frame and converted to MP4 using FFmpeg.

IMPORTANT REQUIREMENTS:

1. Generate actual HTML5, CSS3 and JavaScript.
2. Do NOT merely describe the animation.
3. Do NOT write explanations.
4. Do NOT use images unless the scene explicitly requires one.
5. Do NOT use external websites, CDNs, APIs or external assets.
6. Everything must work offline.
7. Use CSS shapes, gradients, text, pseudo-elements and JavaScript
   when appropriate.
8. The canvas must be exactly 1080x1920.
9. The scene must fill the complete 1080x1920 viewport.
10. Text must be clearly visible.
11. Animations must use real CSS @keyframes or JavaScript.
12. The code must work inside Chromium.
13. Do NOT use video-generation APIs.
14. Do NOT use canvas libraries.
15. Do NOT use React.
16. Do NOT use Tailwind.
17. Keep the code completely self-contained.
18. Do NOT use external fonts.
19. Do NOT use external images.
20. Do NOT use fetch().
21. Do NOT use axios.
22. Do NOT use XMLHttpRequest.
23. Do NOT use WebSocket.
24. Do NOT use external API calls.
25. Do NOT include Markdown code fences.
26. Return ONLY the complete HTML document.

=========================================================
VIDEO FORMAT
=========================================================

Resolution:
1080 x 1920

Aspect Ratio:
9:16

Rendering:
Chromium + Playwright

Frame Rate:
30 FPS

The scene must completely fill the viewport.

=========================================================
SCENE INFORMATION
=========================================================

Scene ID:
{scene.scene_id}

Duration:
{scene.duration} seconds

Background:
{scene.background}

Visual Type:
{scene.visual_type}

Image Required:
{scene.image_required}

Image Description:
{scene.image_description}

Main Text:
{scene.text}

Text Position:
{scene.text_position}

Animation:
{scene.animation}

Transition:
{scene.transition}

Effects:
{scene.effects}

=========================================================
VISUAL QUALITY REQUIREMENTS
=========================================================

The scene should look like a polished modern
short-form informational video.

Use appropriate combinations of:

- strong typography
- good spacing
- visual hierarchy
- layered backgrounds
- gradients
- CSS shapes
- cards
- icons using CSS where appropriate
- diagrams
- lines
- circles
- particles using CSS/JavaScript
- glow
- shadows
- depth
- subtle motion
- smooth transitions
- scale animations
- opacity animations
- position animations
- rotation
- blur
- staggered animations

Do NOT simply place plain text in the center.

The visual design must actually communicate the
meaning of the scene.

=========================================================
ANIMATION REQUIREMENTS
=========================================================

Animations must work automatically when the page loads.

Do NOT require:

- mouse interaction
- keyboard input
- clicking
- scrolling
- user interaction

The scene must play automatically.

If JavaScript is required, keep it self-contained.

CSS @keyframes are preferred for simple animations.

=========================================================
OFFLINE REQUIREMENTS
=========================================================

The scene must work completely offline.

Do NOT include:

<script src="https://...">

<link href="https://...">

@import url("https://...")

fetch("https://...")

axios requests

API requests

external CDNs

external fonts

external libraries

=========================================================
HTML STRUCTURE
=========================================================

Return a complete HTML document containing:

<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=1080,height=1920"
    >

    <style>
        ...
    </style>

</head>

<body>

    ...

    <script>
        ...
    </script>

</body>

</html>

=========================================================
IMPORTANT
=========================================================

Generate CODE, not an explanation.

Return ONLY the complete HTML document.

Do NOT write:

"Here is the code"

Do NOT write:

"Sure"

Do NOT write:

"```html"

Do NOT write any explanation before or after the HTML.

The first meaningful output must be:

<!DOCTYPE html>

and the final output must end with:

</html>
"""

    # =====================================================
    # CALL SELECTED LLM
    # =====================================================

    print(
        f"Generating HTML/CSS/JS for Scene "
        f"{scene.scene_id}..."
    )

    try:

        response = llm.invoke(prompt)

    except Exception as e:

        raise RuntimeError(
            f"Scene {scene.scene_id} LLM generation failed: {e}"
        )

    # =====================================================
    # EXTRACT RESPONSE TEXT
    # =====================================================

    code = extract_text_from_response(
        response
    )

    # =====================================================
    # CLEAN GENERATED CODE
    # =====================================================

    code = clean_generated_code(
        code
    )

    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if not code:

        raise ValueError(
            f"LLM returned empty code for "
            f"Scene {scene.scene_id}."
        )

    if "<html" not in code.lower():

        raise ValueError(
            f"Generated response for Scene "
            f"{scene.scene_id} does not contain "
            f"an HTML document."
        )

    if "<head" not in code.lower():

        raise ValueError(
            f"Generated response for Scene "
            f"{scene.scene_id} does not contain <head>."
        )

    if "<body" not in code.lower():

        raise ValueError(
            f"Generated response for Scene "
            f"{scene.scene_id} does not contain <body>."
        )

    if "</html>" not in code.lower():

        raise ValueError(
            f"Generated response for Scene "
            f"{scene.scene_id} does not contain </html>."
        )

    return code


# =========================================================
# SAVE SCENE CODE
# =========================================================

def save_scene_code(scene_id, code):
    """
    Save generated scene HTML to:

        output/generated_scenes/scene_XX.html
    """

    output_dir = Path(
        "output/generated_scenes"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        output_dir /
        f"scene_{scene_id:02d}.html"
    )

    file_path.write_text(
        code,
        encoding="utf-8"
    )

    return file_path


# =========================================================
# MODULE TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print("CODE GENERATOR AGENT")
    print("========================================")

    print(
        "Provider-aware implementation: READY"
    )

    print(
        "LLM is supplied by main.py."
    )

    print(
        "No provider is hard-coded in this module."
    )

    print("========================================")