Document.addEventListener("DOMContentLoaded", () => {
    // 1. CONFIGURATION
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    let lastScanData = null;
    const synth = window.speechSynthesis;
    
    // Flag to track if the current response should be spoken
    let shouldSpeakResponse = false; 

    console.log("Nexora AI: Neural Core Synced");

    // --- 2. SCROLL REVEAL & UI ---
    const revealOptions = { threshold: 0.15, rootMargin: "0px 0px -50px 0px" };
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, revealOptions);
    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    window.toggleChat = () => {
        const sidePanel = document.getElementById('sidePanel');
        const mainArea = document.getElementById('mainArea');
        sidePanel.classList.toggle('open');
        if (window.innerWidth > 1024) mainArea.classList.toggle('shrunk');
    };

    // --- 3. NEURAL SCANNER LOGIC ---
    window.scanURL = async function() {
        const input = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = input.value.trim();

        if (url.length < 4) {
            display.innerHTML = `<span style="color:var(--danger)">URL too short.</span>`;
            return;
        }

        display.innerHTML = `<span class="loading-text">INTERROGATING NEURAL DATABASE...</span>`;

        try {
            const response = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });
            const data = await response.json();
            lastScanData = data;

            if (data.is_scam) {
                card.className = "scanner-card danger-glow";
                display.innerHTML = `<div style="color:var(--danger); font-weight:800;">⚠️ THREAT DETECTED</div><div>${data.message}</div>`;
            } else {
                card.className = "scanner-card success-glow";
                display.innerHTML = `<div style="color:var(--success); font-weight:800;">✅ DOMAIN SECURE</div><div>Neural integrity verified.</div>`;
            }
        } catch (err) {
            display.innerHTML = `<span style="color:var(--danger)">CONNECTION LOST</span>`;
        }
    };

    // --- 4. VOICE & STREAMING AI ASSISTANT ---

    window.nexoraSpeak = function(text) {
        // ONLY SPEAK IF isVoiceMode was triggered
        if (!shouldSpeakResponse) return; 

        synth.cancel(); 
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.1;
        utterance.pitch = 0.8;
        const voices = synth.getVoices();
        utterance.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
        synth.speak(utterance);
        
        // Reset the flag after speaking
        shouldSpeakResponse = false; 
    };

    window.startVoice = function() {
        const micBtn = document.getElementById('micBtn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) return alert("Voice recognition not supported.");

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micBtn.classList.add('listening');
            shouldSpeakResponse = true; // SET FLAG TO TRUE FOR VOICE
        };
        recognition.onend = () => micBtn.classList.remove('listening');

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            window.sendChatMessage(true); // Pass true because it's voice
        };
        recognition.start();
    };

    window.sendChatMessage = async function(isFromVoice = false) {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        const msg = input.value.trim();
        
        if (!msg) return;

        // If user typed and hit enter, make sure flag is false
        if (!isFromVoice) shouldSpeakResponse = false;

        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
        input.value = '';
        
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'ai-msg';
        aiMsgDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content"></span><span class="typing-cursor"></span>`;
        box.appendChild(aiMsgDiv);

        const contentSpan = aiMsgDiv.querySelector('.ai-content');
        const cursor = aiMsgDiv.querySelector('.typing-cursor');

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponseText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                fullResponseText += chunk;
                contentSpan.innerText = fullResponseText;
                box.scrollTop = box.scrollHeight;
            }

            cursor.remove();
            
            // This function now checks the flag internally
            window.nexoraSpeak(fullResponseText); 

        } catch (err) {
            cursor.remove();
            contentSpan.innerHTML = `<span style="color:var(--danger)">AI offline.</span>`;
        }
        box.scrollTop = box.scrollHeight;
    };

    // --- 5. EVENT LISTENERS ---
    document.getElementById('urlInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
    
    document.getElementById('chatInput').addEventListener('keypress', (e) => { 
        if (e.key === 'Enter') {
            shouldSpeakResponse = false; // Typed input = Silence
            sendChatMessage(false); 
        }
    });
});
