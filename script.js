document.addEventListener("DOMContentLoaded", () => {
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    // --- REVEAL SAFETY ---
    const forceShow = () => {
        document.querySelectorAll('.reveal').forEach(el => el.classList.add('active'));
    };
    forceShow();

    // --- UI CONTROLS ---
    window.toggleChat = () => {
        document.getElementById('sidePanel')?.classList.toggle('open');
    };

    window.nexoraSpeak = function(text) {
        if (!shouldSpeakResponse) return; 
        synth.cancel(); 
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        const voices = synth.getVoices();
        utterance.voice = voices.find(v => v.name.includes('Male')) || voices[0];
        synth.speak(utterance);
        shouldSpeakResponse = false; 
    };

    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice not supported.");
        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            document.getElementById('micBtn')?.classList.add('listening');
            shouldSpeakResponse = true; 
        };
        recognition.onresult = (event) => {
            document.getElementById('chatInput').value = event.results[0][0].transcript;
            window.sendChatMessage(true); 
        };
        recognition.start();
    };

    // --- CHAT ENGINE ---
    window.sendChatMessage = async function(isFromVoice = false) {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        if (!input || !box || !input.value.trim()) return;

        shouldSpeakResponse = isFromVoice; 
        const msg = input.value;
        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
        input.value = '';

        const aiDiv = document.createElement('div');
        aiDiv.className = 'ai-msg';
        aiDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content">...</span>`;
        box.appendChild(aiDiv);
        box.scrollTop = box.scrollHeight;

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg, is_voice: isFromVoice })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";
            const contentSpan = aiDiv.querySelector('.ai-content');

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                if (fullText === "") contentSpan.innerText = "";
                fullText += decoder.decode(value);
                contentSpan.innerText = fullText;
                box.scrollTop = box.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            aiDiv.querySelector('.ai-content').innerText = "System offline. Wake up Render.";
        }
    };

    // --- SCANNER ---
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

    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { shouldSpeakResponse = false; sendChatMessage(false); }
    });
});
