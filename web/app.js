const $ = id => document.getElementById(id);

const topic = $('topic');
const duration = $('duration');
const tone = $('tone');
const audience = $('audience');
const provider = $('provider');
const apiKey = $('apiKey');
const model = $('model');
const baseUrl = $('baseUrl');
const codeModel = $('codeModel');
const apiGroup = $('apiGroup');
const customGroup = $('customGroup');

const generateScriptBtn = $('generateScriptBtn');
const scriptPanel = $('scriptPanel');
const scriptContent = $('scriptContent');
const scriptMeta = $('scriptMeta');
const scriptStatus = $('scriptStatus');
const editBox = $('editBox');
const editInstruction = $('editInstruction');
const videoDecisionPanel = $('videoDecisionPanel');
const statusPanel = $('statusPanel');
const stage = $('stage');
const progressText = $('progressText');
const progressBar = $('progressBar');
const logs = $('logs');
const resultPanel = $('resultPanel');
const video = $('video');
const downloadBtn = $('downloadBtn');
const errorPanel = $('errorPanel');

let currentJobId = null;
let currentScript = null;

function updateProviderUI() {
    apiGroup.classList.toggle('hidden', provider.value === 'local');
    customGroup.classList.toggle('hidden', provider.value !== 'custom');
}

provider.addEventListener('change', updateProviderUI);
updateProviderUI();

function showError(message) {
    errorPanel.textContent = message;
    errorPanel.classList.remove('hidden');
}

function clearError() {
    errorPanel.classList.add('hidden');
    errorPanel.textContent = '';
}

function setBusy(button, busy, text) {
    button.disabled = busy;
    if (text) button.textContent = text;
}

function resetRunUI() {
    clearError();
    statusPanel.classList.remove('hidden');
    resultPanel.classList.add('hidden');
    videoDecisionPanel.classList.add('hidden');
    logs.textContent = '';
    progressBar.style.width = '2%';
    progressText.textContent = '2%';
    stage.textContent = 'Starting...';
}

function esc(value) {
    const d = document.createElement('div');
    d.textContent = value ?? '';
    return d.innerHTML;
}

function scriptStatusValue(script) {
    return script?.status || 'READY';
}

function renderScript(script) {
    currentScript = script;
    scriptPanel.classList.remove('hidden');
    scriptStatus.textContent = scriptStatusValue(script);

    scriptMeta.innerHTML = `
        <div><b>Title</b><span>${esc(script.title)}</span></div>
        <div><b>Duration</b><span>${Number(script.total_duration) || 0}s</span></div>
        <div><b>Tone</b><span>${esc(script.tone)}</span></div>
        <div><b>Audience</b><span>${esc(script.audience)}</span></div>
    `;

    let html = `<div class="hook"><b>Hook</b><p>${esc(script.hook)}</p></div>`;

    (script.scenes || []).forEach(scene => {
        const dialogues = (scene.dialogues || [])
            .map(d => `<div class="dialogue"><strong>${esc(d.character)}:</strong> ${esc(d.line)}</div>`)
            .join('');

        html += `
            <article class="scene-card">
                <div class="scene-top">
                    <span>Scene ${esc(scene.scene_id)}</span>
                    <span>${esc(scene.duration)}s</span>
                </div>
                <div class="scene-body">
                    <div><b>Narration</b><p>${esc(scene.narration)}</p></div>
                    ${dialogues ? `<div><b>Dialogue</b>${dialogues}</div>` : ''}
                    <div><b>Visual direction</b><p>${esc(scene.visual_direction)}</p></div>
                    ${scene.on_screen_text ? `<div><b>On-screen text</b><p>${esc(scene.on_screen_text)}</p></div>` : ''}
                </div>
            </article>
        `;
    });

    if (script.cta) {
        html += `<div class="cta"><b>CTA</b><p>${esc(script.cta)}</p></div>`;
    }

    scriptContent.innerHTML = html;
}

function validateInputs() {
    clearError();

    if (!topic.value.trim()) return 'Please enter a video topic.';

    const d = Number(duration.value);
    if (!Number.isFinite(d) || d < 5 || d > 1800) {
        return 'Duration must be between 5 and 1800 seconds.';
    }

    if (provider.value !== 'local' && !apiKey.value.trim()) {
        return 'Please enter your API key.';
    }

    if (provider.value === 'custom' && (!model.value.trim() || !baseUrl.value.trim())) {
        return 'Custom provider requires both model and base URL.';
    }

    return null;
}

function commonPayload() {
    return {
        topic: topic.value.trim(),
        duration: Number(duration.value),
        tone: tone.value.trim(),
        audience: audience.value.trim(),
        provider: provider.value,
        api_key: apiKey.value.trim(),
        model: model.value.trim(),
        base_url: baseUrl.value.trim(),
        code_model: codeModel.value.trim()
    };
}

async function requestJSON(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        },
        ...options
    });

    let data = {};
    try {
        data = await response.json();
    } catch (_) {
        // Keep the generic HTTP error below.
    }

    if (!response.ok) {
        throw new Error(data.detail || data.error || 'Request failed.');
    }

    return data;
}

async function generateScript() {
    const error = validateInputs();
    if (error) {
        showError(error);
        return;
    }

    resetRunUI();
    scriptPanel.classList.add('hidden');
    setBusy(generateScriptBtn, true, 'Generating Script...');

    try {
        const data = await requestJSON('/api/script', {
            method: 'POST',
            body: JSON.stringify(commonPayload())
        });

        currentJobId = data.job_id;
        await pollScript(data.job_id);
    } catch (e) {
        showError(e.message);
        setBusy(generateScriptBtn, false, 'Generate Script');
    }
}

async function pollScript(jobId) {
    const data = await requestJSON(`/api/script/${jobId}`);

    stage.textContent = data.stage || 'Writing script...';
    const progress = Number(data.progress || 0);
    progressText.textContent = `${progress}%`;
    progressBar.style.width = `${progress}%`;
    logs.textContent = (data.logs || []).join('\n');
    logs.scrollTop = logs.scrollHeight;

    if (data.status === 'completed' && data.script) {
        renderScript(data.script);
        statusPanel.classList.add('hidden');
        setBusy(generateScriptBtn, false, 'Generate Script');
        return;
    }

    if (data.status === 'failed') {
        throw new Error(data.error || 'Script generation failed.');
    }

    if (data.status === 'cancelled') {
        setBusy(generateScriptBtn, false, 'Generate Script');
        return;
    }

    setTimeout(() => {
        pollScript(jobId).catch(e => {
            showError(e.message);
            setBusy(generateScriptBtn, false, 'Generate Script');
        });
    }, 800);
}

$('editScriptBtn').addEventListener('click', () => {
    editBox.classList.remove('hidden');
    editInstruction.focus();
});

$('cancelEditBtn').addEventListener('click', () => {
    editBox.classList.add('hidden');
});

$('applyEditBtn').addEventListener('click', async () => {
    if (!currentJobId || !editInstruction.value.trim()) {
        showError('Enter what you want to change.');
        return;
    }

    try {
        setBusy($('applyEditBtn'), true, 'Updating...');
        const data = await requestJSON(`/api/script/${currentJobId}/edit`, {
            method: 'POST',
            body: JSON.stringify({ instruction: editInstruction.value.trim() })
        });

        renderScript(data.script);
        editInstruction.value = '';
        editBox.classList.add('hidden');
    } catch (e) {
        showError(e.message);
    } finally {
        setBusy($('applyEditBtn'), false, 'Apply Edit');
    }
});

$('regenerateScriptBtn').addEventListener('click', async () => {
    if (!currentJobId) return;

    try {
        setBusy($('regenerateScriptBtn'), true, 'Regenerating...');
        const data = await requestJSON(`/api/script/${currentJobId}/regenerate`, {
            method: 'POST'
        });
        renderScript(data.script);
    } catch (e) {
        showError(e.message);
    } finally {
        setBusy($('regenerateScriptBtn'), false, 'Regenerate');
    }
});

$('cancelScriptBtn').addEventListener('click', async () => {
    if (currentJobId) {
        try {
            await requestJSON(`/api/script/${currentJobId}/cancel`, { method: 'POST' });
        } catch (_) {
            // Cancellation is still treated as a local UI stop.
        }
    }

    scriptPanel.classList.add('hidden');
    videoDecisionPanel.classList.add('hidden');
    statusPanel.classList.add('hidden');
    currentScript = null;
    currentJobId = null;
    setBusy(generateScriptBtn, false, 'Generate Script');
});

$('approveScriptBtn').addEventListener('click', async () => {
    if (!currentJobId) return;

    try {
        setBusy($('approveScriptBtn'), true, 'Approving...');
        const data = await requestJSON(`/api/script/${currentJobId}/approve`, {
            method: 'POST'
        });
        renderScript(data.script || currentScript);
        videoDecisionPanel.classList.remove('hidden');
        videoDecisionPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (e) {
        showError(e.message);
    } finally {
        setBusy($('approveScriptBtn'), false, 'Approve Script');
    }
});

$('saveScriptBtn').addEventListener('click', async () => {
    if (!currentJobId) return;

    try {
        setBusy($('saveScriptBtn'), true, 'Saving...');
        const data = await requestJSON(`/api/script/${currentJobId}/save`, {
            method: 'POST'
        });
        videoDecisionPanel.innerHTML = `
            <span class="eyebrow">SCRIPT SAVED</span>
            <h2>Your approved script has been saved.</h2>
            <p>${esc(data.path || 'Script saved successfully.')}</p>
        `;
    } catch (e) {
        showError(e.message);
    } finally {
        setBusy($('saveScriptBtn'), false, 'No, Save Script');
    }
});

$('generateVideoBtn').addEventListener('click', async () => {
    if (!currentJobId) return;

    try {
        resetRunUI();
        setBusy($('generateVideoBtn'), true, 'Starting Video...');
        const data = await requestJSON(`/api/script/${currentJobId}/video`, {
            method: 'POST'
        });
        currentJobId = data.job_id || currentJobId;
        await pollVideo(currentJobId);
    } catch (e) {
        showError(e.message);
        setBusy($('generateVideoBtn'), false, 'Yes, Generate Video');
    }
});

async function pollVideo(jobId) {
    const data = await requestJSON(`/api/jobs/${jobId}`);
    const progress = Number(data.progress || 0);

    stage.textContent = data.stage || 'Working...';
    progressText.textContent = `${progress}%`;
    progressBar.style.width = `${progress}%`;
    logs.textContent = (data.logs || []).join('\n');
    logs.scrollTop = logs.scrollHeight;

    if (data.status === 'completed') {
        const url = `/api/jobs/${jobId}/video`;
        video.src = url;
        downloadBtn.href = url;
        resultPanel.classList.remove('hidden');
        setBusy($('generateVideoBtn'), false, 'Yes, Generate Video');
        return;
    }

    if (data.status === 'failed') {
        throw new Error(data.error || 'Video generation failed.');
    }

    setTimeout(() => {
        pollVideo(jobId).catch(e => {
            showError(e.message);
            setBusy($('generateVideoBtn'), false, 'Yes, Generate Video');
        });
    }, 1200);
}

generateScriptBtn.addEventListener('click', generateScript);
