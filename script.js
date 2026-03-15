document.addEventListener("DOMContentLoaded", () => {
    // --- CONFIGURATION ---
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth = window.speechSynthesis;
    let shouldSpeakResponse = false;

    // --- 1. INSTANT UI REVEAL (Fixes Black Screen) ---
    const forceReveal = () => {
        document.querySelectorAll('.reveal').forEach(el => {
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
            el.classList.add('active');
        });
    };
    forceReveal();
    setTimeout(forceReveal, 500); // Safety backup

    // --- 2. BACKEND WAKE-UP (Infinite Engine) ---
    async function igniteSystems() {
        try {
            await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: "ping.com" })
            });
            console.log("Nexora: Neural Link Established.");
        } catch (e) {
            console.log("Nexora: Reconnecting to Core...");
        }
    }
    igniteSystems();

    // --- 3. UI CONTROLS ---
    window.toggleChat = () => {
        const panel = document.getElementById('sidePanel');
        if (panel) panel.classList.toggle('open');
    };

    // --- 4. VOICE ENGINE ---
    window.nexoraSpeak = function(text) {
        if (!shouldSpeakResponse) return;
        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = synth.getVoices();
        // Priority for a professional male voice
        utterance.voice = voices.find(v => v.name.includes('Male')) || voices[0];
        utterance.rate = 1.0;
        synth.speak(utterance);
        shouldSpeakResponse = false;
    };

    window.startVoice = function() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Speech recognition not supported in this browser.");
        
        const recognition = new SpeechRecognition();
        recognition.onstart = () => {
            document.getElementById('micBtn')?.classList.add('listening');
            shouldSpeakResponse = true;
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            window.sendChatMessage(true);
            document.getElementById('micBtn')?.classList.remove('listening');
        };
        recognition.onerror = () => document.getElementById('micBtn')?.classList.remove('listening');
        recognition.start();
    };

    // --- 5. SCANNER ENGINE (INFINITE SECURITY) ---
    window.scanURL = async function() {
        const urlIn = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        if (!urlIn || !display) return;
        
        // Show Round Spinner
        display.innerHTML = `<div class="spinner"></div> ANALYZING DNA...`;

        try {
            const res = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlIn.value })
            });
            const data = await res.json();
            
            if (data.is_scam) {
                display.innerHTML = `<span style="color: #ff4d4d; font-weight: bold;">⚠️ ${data.message}</span>`;
            } else {
                display.innerHTML = `<span style="color: #00ff88; font-weight: bold;">✅ SECURE</span>`;
            }
        } catch (e) { 
            display.innerHTML = `<span style="color: #ffcc00;">OFFLINE: Wake up Backend</span>`;
            igniteSystems(); // Auto-retry wake up
        }
    };

    // --- 6. CHAT ENGINE (RAPID STREAMING) ---
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
        // Initial state with Round Spinner
        aiDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content"><div class="spinner"></div></span>`;
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
            let firstChunk = true;

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                // Speed optimization: Clear spinner immediately on first arrival of text
                if (firstChunk) {
                    contentSpan.innerHTML = "";
                    firstChunk = false;
                }

                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;
                contentSpan.innerText = fullText;
                box.scrollTop = box.scrollHeight;
            }
            
            if (shouldSpeakResponse) window.nexoraSpeak(fullText);

        } catch (err) {
            aiDiv.querySelector('.ai-content').innerText = "Neural Link timed out.";
        }
    };

    // Event Listener for Enter Key
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            shouldSpeakResponse = false;
            sendChatMessage(false);
        }
    });
});
