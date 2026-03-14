document.addEventListener("DOMContentLoaded", () => {
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: Core Online");

    // --- UI CONTROLS ---
    window.toggleChat = () => {
        const sidePanel = document.getElementById('sidePanel');
        if (sidePanel) sidePanel.classList.toggle('open');
    };

    // --- VOICE LOGIC ---
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

    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice not supported.");
        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            document.getElementById('micBtn').classList.add('listening');
            shouldSpeakResponse = true; 
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            window.sendChatMessage(true); 
        };
        recognition.start();
    };

    // --- CHAT LOGIC ---
    window.sendChatMessage = async function(isFromVoice = false) {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        const msg = input.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice; 
        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
        input.value = '';
        
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'ai-msg';
        aiMsgDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content"></span>`;
        box.appendChild(aiMsgDiv);

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
                aiMsgDiv.querySelector('.ai-content').innerText = fullText;
                box.scrollTop = box.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            aiMsgDiv.querySelector('.ai-content').innerText = "Connection lost.";
        }
    };

    // --- SCANNER LOGIC ---
    window.scanURL = async function() {
        const url = document.getElementById('urlInput').value.trim();
        const display = document.getElementById('result-display');
        if (!url) return;
        display.innerHTML = "SCANNING...";
        try {
            const res = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });
            const data = await res.json();
            display.innerHTML = data.is_scam ? `⚠️ ${data.message}` : `✅ SECURE`;
        } catch (e) { display.innerHTML = "Offline."; }
    };

    // --- EVENT LISTENERS ---
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false;
            sendChatMessage(false);
        }
    });
});
