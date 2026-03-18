const form = document.getElementById('storyForm');
const generateBtn = document.getElementById('generateBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const statusMsg = document.getElementById('statusMessage');
const stepsContainer = document.getElementById('workflowSteps');
const finalOutput = document.getElementById('finalOutput');
const videoPlayer = document.getElementById('videoPlayer');
const downloadLink = document.getElementById('downloadLink');

// Define known workflow steps for visualization
const WORKFLOW_STEPS = [
    'story_analyst', 'scriptwriter', 'character_designer', 
    'director', 'animator', 'audio_engineer', 'editor', 'critic'
];

function resetUI() {
    stepsContainer.innerHTML = '';
    WORKFLOW_STEPS.forEach(step => {
        const div = document.createElement('div');
        div.id = `step-${step}`;
        div.className = 'step-item p-3 bg-gray-900 rounded border border-gray-700 flex justify-between items-center transition-all duration-300';
        div.innerHTML = `
            <span class="font-mono text-sm capitalize">${step.replace('_', ' ')}</span>
            <span class="status-icon text-gray-500">○</span>
        `;
        stepsContainer.appendChild(div);
    });
    finalOutput.classList.add('hidden');
    statusMsg.innerText = '';
    statusMsg.className = 'text-center text-sm font-mono mt-2 min-h-[20px]';
}

function updateStepStatus(stepName, status) {
    const el = document.getElementById(`step-${stepName}`);
    if (!el) return;

    const icon = el.querySelector('.status-icon');
    if (status === 'running') {
        el.className = 'step-item p-3 bg-blue-900/30 border border-blue-500 rounded flex justify-between items-center';
        icon.className = 'status-icon text-blue-400 animate-pulse';
        icon.innerText = '●'; // In progress
    } else if (status === 'done') {
        el.className = 'step-item p-3 bg-green-900/30 border border-green-500 rounded flex justify-between items-center';
        icon.className = 'status-icon text-green-400';
        icon.innerText = '✓'; // Done
    }
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const story = document.getElementById('storyInput').value;
    if (!story) return;

    // UI Loading State
    generateBtn.disabled = true;
    btnText.innerText = "Production in Progress...";
    btnSpinner.classList.remove('hidden');
    resetUI();

    try {
        // Start Job via JSON POST
        const res = await fetch('/generate/episode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({story_text: story})
        });

        if (!res.ok) {
            throw new Error(`API Error: ${res.statusText}`);
        }
        
        const data = await res.json();
        const jobId = data.job_id;
        
        statusMsg.innerText = `Job ID: ${jobId}. Connecting to stream...`;
        statusMsg.classList.add('text-blue-400');

        // Connect WebSocket
        const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const ws = new WebSocket(`${proto}://${window.location.host}/ws/status/${jobId}`);

        ws.onmessage = (event) => {
            const msg = event.data;
            if (msg.includes("finished")) {
                const nodeName = msg.split("'")[1];
                updateStepStatus(nodeName, 'done');
            } else if (msg.includes("Starting")) {
                 statusMsg.innerText = msg;
            } else if (msg.includes("Pipeline Finished")) {
                // Done
                btnText.innerText = "Generate Episode";
                btnSpinner.classList.add('hidden');
                generateBtn.disabled = false;
                statusMsg.innerText = "Production Complete!";
                statusMsg.className = "text-center text-sm font-mono mt-2 text-green-400 font-bold";
                
                // Show Result (Dummy path for MVP if real file not served)
                finalOutput.classList.remove('hidden');
                // Download link would need real path
                downloadLink.href = "/assets/output/episode_1_final.mp4"; 
            }
        };

        ws.onclose = () => {
            console.log("WS Closed");
        };

    } catch (err) {
        console.error(err);
        statusMsg.innerText = "Error initiating production.";
        statusMsg.classList.add('text-red-500');
        generateBtn.disabled = false;
        btnText.innerText = "Generate Episode";
        btnSpinner.classList.add('hidden');
    }
});
