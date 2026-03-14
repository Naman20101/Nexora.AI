document.addEventListener("DOMContentLoaded", () => {
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: System Initializing...");

    // --- SAFETY CHECK: Ensure UI exists ---
    const chatInput = document.getElementById('chatInput');
    const chatBox = document.getElementById('chatBox');
    const micBtn = document.getElementById('micBtn');

    // 1. VOICE OUTPUT LOGIC
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

    // 2. VOICE INPUT LOGIC
    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice not supported.");
        
        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            if(micBtn) micBtn.classList.add('listening');
            shouldSpeakResponse = true; 
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if(chatInput) chatInput.value = transcript;
            window.sendChatMessage(true); 
        };
        recognition.start();
    };

    // 3. CHAT ENGINE (Identity Lock Included)
    window.sendChatMessage = async function(isFromVoice = false) {
        if (!chatInput || !chatBox) return;
        const msg = chatInput.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice; 
        chatBox.innerHTML += `<div class="user-msg"><b>Naman:</b> ${msg}</div>`;
        chatInput.value = '';
        
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'ai-msg';
        aiMsgDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content">Connecting...</span>`;
        chatBox.appendChild(aiMsgDiv);

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
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            aiMsgDiv.querySelector('.ai-content').innerText = "Backend is sleeping. Please wait 30s.";
        }
    };

    // 4. SCANNER LOGIC
    window.scanURL = async function() {
        const urlIn = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        if (!urlIn || !display) return;
        display.innerHTML = "ANALYZING...";
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

    // 5. EVENT LISTENERS
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false;
            sendChatMessage(false);
        }
    });
});
