document.addEventListener("DOMContentLoaded", () => {
    // 1. BACKEND SYNC
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: System Booting...");

    // 2. UI ELEMENTS (Safeguard against null)
    const chatInput = document.getElementById('chatInput');
    const urlInput = document.getElementById('urlInput');
    const chatBox = document.getElementById('chatBox');

    // --- 3. IDENTITY & VOICE LOGIC ---
    window.nexoraSpeak = function(text) {
        if (!shouldSpeakResponse) return; 
        
        synth.cancel(); 
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 0.9;
        
        // Identity Lock for Naman Reddy's AI
        const voices = synth.getVoices();
        utterance.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
        
        synth.speak(utterance);
        shouldSpeakResponse = false; // Reset flag
    };

    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice recognition not supported on this browser.");

        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            document.getElementById('micBtn')?.classList.add('listening');
            shouldSpeakResponse = true; // Permitted to talk
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (chatInput) chatInput.value = transcript;
            window.sendChatMessage(true); 
        };
        recognition.start();
    };

    // --- 4. CHAT ENGINE ---
    window.sendChatMessage = async function(isFromVoice = false) {
        if (!chatInput || !chatBox) return;
        const msg = chatInput.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice; // Voice in = Voice out
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
            const contentSpan = aiMsgDiv.querySelector('.ai-content');

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                fullText += decoder.decode(value);
                contentSpan.innerText = fullText;
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            aiMsgDiv.querySelector('.ai-content').innerText = "Neural link severed. Wake up Render backend.";
        }
    };

    // --- 5. SCANNER ENGINE ---
    window.scanURL = async function() {
        const display = document.getElementById('result-display');
        if (!urlInput || !display) return;
        
        const url = urlInput.value.trim();
        display.innerHTML = "ANALYZING...";

        try {
            const res = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });
            const data = await res.json();
            display.innerHTML = data.is_scam ? `⚠️ THREAT: ${data.message}` : `✅ SECURE`;
        } catch (e) {
            display.innerHTML = "Backend sleeping. Wake it up first.";
        }
    };

    // --- 6. GLOBAL CONTROLS ---
    window.toggleChat = () => {
        document.getElementById('sidePanel')?.classList.toggle('open');
    };

    // Event Listeners for Enter Keys
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false; // Typing is silent
            sendChatMessage(false);
        }
    });

    urlInput?.addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
});
