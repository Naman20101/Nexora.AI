document.addEventListener("DOMContentLoaded", () => {
    // 1. CONFIGURATION
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: System Booting...");

    // --- 2. THE BLACK SCREEN KILLER ---
    // This forces the UI to be visible even if the rest of the script fails.
    const forceVisibility = () => {
        const elements = document.querySelectorAll('.reveal');
        elements.forEach(el => {
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
            el.classList.add('active');
        });
        const mainArea = document.getElementById('mainArea');
        if (mainArea) mainArea.style.display = "block";
    };
    forceVisibility(); 

    // --- 3. UI CONTROLS ---
    window.toggleChat = () => {
        const panel = document.getElementById('sidePanel');
        if (panel) panel.classList.toggle('open');
    };

    // --- 4. VOICE OUTPUT (TTS) ---
    window.nexoraSpeak = function(text) {
        if (!shouldSpeakResponse) return; 
        synth.cancel(); 
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        const voices = synth.getVoices();
        utterance.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
        synth.speak(utterance);
        shouldSpeakResponse = false; 
    };

    // --- 5. VOICE INPUT (STT) ---
    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice not supported.");

        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            const mBtn = document.getElementById('micBtn');
            if(mBtn) mBtn.classList.add('listening');
            shouldSpeakResponse = true; 
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input = document.getElementById('chatInput');
            if(input) {
                input.value = transcript;
                window.sendChatMessage(true); 
            }
        };
        recognition.start();
    };

    // --- 6. CHAT ENGINE (With Identity Lock) ---
    window.sendChatMessage = async function(isFromVoice = false) {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        if (!input || !box) return;

        const msg = input.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice; 
        box.innerHTML += `<div class="user-msg"><b>Naman:</b> ${msg}</div>`;
        input.value = '';

        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'ai-msg';
        aiMsgDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content">...</span>`;
        box.appendChild(aiMsgDiv);
        box.scrollTop = box.scrollHeight;

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                fullText += decoder.decode(value);
                const content = aiMsgDiv.querySelector('.ai-content');
                if(content) content.innerText = fullText;
                box.scrollTop = box.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            console.error("Connection Error");
        }
    };

    // --- 7. URL SCANNER ---
    window.scanURL = async function() {
        const urlIn = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        if (!urlIn || !display) return;
        display.innerHTML = "INTERROGATING NEURAL CORE...";
        try {
            const res = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlIn.value })
            });
            const data = await res.json();
            display.innerHTML = data.is_scam ? `⚠️ ${data.message}` : `✅ SECURE`;
        } catch (e) { display.innerHTML = "Offline."; }
    };

    // Listen for Enter Key
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false;
            sendChatMessage(false);
        }
    });
});
