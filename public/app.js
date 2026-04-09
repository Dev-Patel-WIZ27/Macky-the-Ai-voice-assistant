/**
 * Macky AI – Virtual Assistant
 * Web Frontend Logic (app.js)
 */

const BACKEND_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
    ? "http://localhost:8000" 
    : window.location.origin;

// --- DOM Elements ---
const mackyOrb = document.getElementById('macky-orb');
const statusText = document.getElementById('ai-status-text');
const chatLog = document.getElementById('chat-id');
const micBtn = document.getElementById('mic-btn');
const manualInput = document.getElementById('manual-input');
const sendBtn = document.getElementById('send-btn');
const backendStatus = document.getElementById('backend-status');
const settingsPanel = document.getElementById('settings-panel');
const apiKeyInput = document.getElementById('api-key-input');

// --- State ---
let isListening = false;
let config = {
    apiKey: localStorage.getItem('macky_openai_key') || ""
};

// Initialize API key input
apiKeyInput.value = config.apiKey;

// --- Backend Connection Check ---
async function checkBackend() {
    try {
        const response = await fetch(`${BACKEND_URL}/status`);
        const data = await response.json();
        if (data.status === "online") {
            backendStatus.classList.add('online');
            backendStatus.innerHTML = `<span class="dot"></span> Online (${data.mode})`;
        }
    } catch (e) {
        backendStatus.classList.remove('online');
        backendStatus.innerHTML = `<span class="dot"></span> Backend Offline`;
    }
}
setInterval(checkBackend, 5000);
checkBackend();

// --- Speech Synthesis (Macky Speaking) ---
function say(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.volume = 1;
    speech.rate = 1.0;
    speech.pitch = 0.9; // Slightly deeper Arctic voice
    
    // Choose a professional voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes("Google") || v.lang === "en-US");
    if (preferredVoice) speech.voice = preferredVoice;

    mackyOrb.classList.add('listening'); // Pulse while speaking
    window.speechSynthesis.speak(speech);
    
    speech.onend = () => {
        handleSpeechEnd();
    };
}

// --- Speech Recognition (User Talking) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('active');
        statusText.textContent = "Listening...";
        mackyOrb.classList.add('listening');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        processQuery(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech Error:", event.error);
        stopListening();
    };

    recognition.onend = () => {
        stopListening();
        // Auto-restart listening if awake and not manually stopped
        if (mackyAwake && !isListening) {
             setTimeout(() => { if (mackyAwake && !isListening) micBtn.click(); }, 100);
        }
    };

    micBtn.onclick = () => {
        if (!isListening) {
            recognition.start();
        } else {
            recognition.stop();
        }
    };
} else {
    alert("Web Speech API is not supported in this browser.");
}

function stopListening() {
    isListening = false;
    micBtn.classList.remove('active');
    statusText.textContent = "Awaiting Command";
    mackyOrb.classList.remove('listening');
}

// --- Logic Loop ---
async function processQuery(query) {
    if (!query) return;
    
    addMessage(query, 'user');
    statusText.textContent = "Processing...";

    try {
        const response = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                apikey: config.apiKey,
                local_time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
            })
        });

        const data = await response.json();
        
        handleBackendAction(data);
        addMessage(data.response, 'bot');
        say(data.response);

    } catch (e) {
        const errorMsg = "I'm having trouble connecting to my backend server.";
        addMessage(errorMsg, 'bot');
        say(errorMsg);
    } finally {
        statusText.textContent = "Awaiting Command";
    }
}

function handleBackendAction(data) {
    if (data.type === "shutdown") {
        setTimeout(() => {
            statusText.textContent = "SYSTEM OFFLINE";
            mackyOrb.style.opacity = "0.3";
            micBtn.style.display = "none";
            manualInput.disabled = true;
            addMessage("System: Connection Terminated.", 'bot');
        }, 3000);
    }
    if (data.type === "browser" && data.url) {
        setTimeout(() => {
            window.open(data.url, '_blank');
        }, 1000);
    }
}

// --- UI Helpers ---
function addMessage(text, side) {
    const div = document.createElement('div');
    div.className = `msg ${side}`;
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}

sendBtn.onclick = () => {
    const val = manualInput.value.trim();
    if (val) {
        processQuery(val);
        manualInput.value = "";
    }
};

manualInput.onkeydown = (e) => {
    if (e.key === "Enter") sendBtn.click();
};

// --- Settings ---
window.toggleSettings = () => {
    settingsPanel.style.display = settingsPanel.style.display === 'block' ? 'none' : 'block';
};

window.saveSettings = () => {
    const key = apiKeyInput.value.trim();
    localStorage.setItem('macky_openai_key', key);
    config.apiKey = key;
    toggleSettings();
    addMessage("System: OpenAI Configuration updated.", 'bot');
    say("Configuration updated.");
};

// --- Initialization ---
function greetBoss() {
    const hour = new Date().getHours();
    let wish = "";
    if (hour < 12) wish = "Good morning";
    else if (hour < 17) wish = "Good afternoon";
    else wish = "Good evening";

    const greeting = `${wish} boss; what can I do for you today?`;
    addMessage(greeting, 'bot');
    say(greeting);
}

// --- Wake Up Logic ---
let mackyAwake = false;

function wakeUp() {
    if (mackyAwake) return;
    mackyAwake = true;
    
    // Hide overlay
    const overlay = document.getElementById('wake-up-overlay');
    if (overlay) overlay.classList.add('hidden');
    
    // Greet and Start Mic
    greetBoss();
    
    // Attempt to start mic immediately
    setTimeout(() => {
        if (!isListening && SpeechRecognition) {
            micBtn.click();
        }
    }, 2000);
}

// --- Continuous Listening Support ---
function handleSpeechEnd() {
    mackyOrb.classList.remove('listening');
    if (mackyAwake && !isListening) {
        setTimeout(() => {
            if (mackyAwake && !isListening) micBtn.click();
        }, 500); 
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('wake-up-overlay');
    if (overlay) {
        overlay.addEventListener('click', wakeUp);
        overlay.addEventListener('touchstart', wakeUp);
    }
    
    // Global fallback for any click/touch
    window.addEventListener('mousedown', wakeUp);
    window.addEventListener('touchstart', wakeUp);

    console.log("Macky System Initialized. Awaiting user interaction...");
});
