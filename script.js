document.addEventListener("DOMContentLoaded", () => {
    // 1. CONFIGURATION
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: System Booting. Internal Core: Naman Reddy.");

    // --- 2. REVEAL LOGIC ---
    const revealElements = () => {
        document.querySelectorAll('.reveal').forEach(el => {
            el.classList.add('active');
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
        });
    };
    revealElements();

    // --- 3. UI HELPERS ---
    window.toggleChat = () => {
        const panel = document.getElementById('sidePanel');
        if (panel) panel.classList.toggle('open');
    };

    // --- 4. VOICE OUTPUT ---
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

    // --- 5. VOICE INPUT ---
    window.startVoice = function() {
        const micBtn = document.getElementById('micBtn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Voice not supported.");

        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            if(micBtn) micBtn.classList.add('listening');
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

    // --- 6. CHAT ENGINE (Public Neutral Version) ---
    window.sendChatMessage = async function(isFromVoice = false) {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        if (!input || !box) return;

        const msg = input.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice; 
        // CHANGED: Label is now "You" instead of "Naman" for public users
        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
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
            const contentSpan = aiMsgDiv.querySelector('.ai-content');

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                // Clear the "..." when the first chunk arrives
                if (fullText === "") contentSpan.innerText = "";
                
                fullText += decoder.decode(value);
                contentSpan.innerText = fullText;
                box.scrollTop = box.scrollHeight;
            }
            window.nexoraSpeak(fullText);
        } catch (err) {
            const contentSpan = aiMsgDiv.querySelector('.ai-content');
            if(contentSpan) contentSpan.innerText = "Connection lost. Please try again in a moment.";
        }
    };

    // --- 7. SCANNER LOGIC ---
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
        } catch (e) { display.innerHTML = "Offline. System booting up."; }
    };

    // --- 8. EVENT LISTENERS ---
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false; // Typing remains silent
            sendChatMessage(false);
        }
    });
});
