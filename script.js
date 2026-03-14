document.addEventListener("DOMContentLoaded", () => {
    // 1. CONFIGURATION
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    let lastScanData = null;
    const synth = window.speechSynthesis;

    console.log("Nexora AI: Neural Core Synced");

    // --- 2. HIGH-END SCROLL REVEAL ---
    const revealOptions = { threshold: 0.15, rootMargin: "0px 0px -50px 0px" };
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, revealOptions);

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    // --- 3. UI CONTROLS ---
    window.toggleChat = () => {
        const sidePanel = document.getElementById('sidePanel');
        const mainArea = document.getElementById('mainArea');
        sidePanel.classList.toggle('open');
        if (window.innerWidth > 1024) {
            mainArea.classList.toggle('shrunk');
        }
    };

    // --- 4. NEURAL SCANNER LOGIC ---
    window.scanURL = async function() {
        const input = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = input.value.trim();

        if (url.length < 4) {
            display.innerHTML = `<span style="color:var(--danger)">URL too short for analysis.</span>`;
            return;
        }

        card.style.transform = "scale(0.98)";
        display.innerHTML = `<span class="loading-text">INTERROGATING NEURAL DATABASE...</span>`;
        
        setTimeout(() => card.style.transform = "scale(1)", 150);

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
                display.innerHTML = `
                    <div style="color:var(--danger); font-weight:800;">⚠️ THREAT DETECTED</div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin: 10px 0;">${data.message}</div>
                    <button onclick="downloadReport()" class="report-btn">GENERATE AUDIT PDF</button>`;
            } else {
                card.className = "scanner-card success-glow";
                display.innerHTML = `
                    <div style="color:var(--success); font-weight:800;">✅ DOMAIN SECURE</div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin: 10px 0;">Neural integrity verified. No fraud signatures found.</div>
                    <button onclick="downloadReport()" class="report-btn">DOWNLOAD CERTIFICATE</button>`;
            }
        } catch (err) {
            display.innerHTML = `<span style="color:var(--danger)">CONNECTION LOST: Backend Wake-up Required</span>`;
        }
    };

    // --- 5. VOICE & STREAMING AI ASSISTANT ---

    // A. Nexora Speaks (TTS)
    window.nexoraSpeak = function(text) {
        synth.cancel(); // Stop current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.1;
        utterance.pitch = 0.8;
        const voices = synth.getVoices();
        // Try to find a male/robotic voice, otherwise use default
        utterance.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
        synth.speak(utterance);
    };

    // B. Nexora Listens (STT)
    window.startVoice = function() {
        const micBtn = document.getElementById('micBtn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            alert("Voice recognition not supported.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';

        recognition.onstart = () => micBtn.classList.add('listening');
        recognition.onend = () => micBtn.classList.remove('listening');
        recognition.onerror = () => micBtn.classList.remove('listening');

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            window.sendChatMessage();
        };

        recognition.start();
    };

    // C. High-Speed Chat Logic (Streaming)
    window.sendChatMessage = async function() {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        const msg = input.value.trim();
        
        if (!msg) return;

        // Add User Bubble
        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
        input.value = '';
        
        // Prepare AI Bubble with Cursor
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'ai-msg';
        aiMsgDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content"></span><span class="typing-cursor"></span>`;
        box.appendChild(aiMsgDiv);
        box.scrollTop = box.scrollHeight;

        const contentSpan = aiMsgDiv.querySelector('.ai-content');
        const cursor = aiMsgDiv.querySelector('.typing-cursor');

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });

            // Read Stream Data
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponseText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                fullResponseText += chunk;
                
                // Update UI word-by-word
                contentSpan.innerText = fullResponseText;
                box.scrollTop = box.scrollHeight;
            }

            // Finish up
            cursor.remove();
            window.nexoraSpeak(fullResponseText); // AI speaks the final result

        } catch (err) {
            cursor.remove();
            contentSpan.innerHTML = `<span style="color:var(--danger)">Neural link severed. AI offline.</span>`;
        }
        box.scrollTop = box.scrollHeight;
    };

    // --- 6. UTILITIES ---
    window.downloadReport = function() {
        if (!lastScanData) return;
        const reportContent = `NEXORA.AI SECURITY AUDIT\nURL: ${lastScanData.url}\nRESULT: ${lastScanData.is_scam ? "MALICIOUS" : "SAFE"}\nCODE: ${lastScanData.prediction_code}\nDATE: ${new Date().toLocaleString()}`;
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = "Nexora_Security_Audit.txt";
        link.click();
    };

    // Search Logic
    const apps = [
        { name: "Paytm", country: "India", website: "https://paytm.com" },
        { name: "PayPal", country: "Global", website: "https://paypal.com" },
        { name: "PhonePe", country: "India", website: "https://phonepe.com" },
        { name: "Venmo", country: "USA", website: "https://venmo.com" }
    ];

    document.getElementById("searchInput")?.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const suggestions = document.getElementById("suggestions");
        suggestions.innerHTML = "";
        if (query.length < 2) return;

        apps.filter(a => a.name.toLowerCase().includes(query)).forEach(app => {
            const div = document.createElement("div");
            div.className = "suggestion-item reveal active";
            div.innerHTML = `<span>${app.name}</span> <a href="${app.website}" target="_blank">OFFICIAL</a>`;
            suggestions.appendChild(div);
        });
    });

    // Handle Enter Keys
    document.getElementById('urlInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
    document.getElementById('chatInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChatMessage(); });
});
// Variable to track how the user sent the message
let isVoiceMode = false;

// Call this when the Voice Button is clicked
function startVoiceInput() {
    isVoiceMode = true;
    // ... your voice recognition code ...
}

// Call this when the Send/Enter Button is clicked
function startTextInput() {
    isVoiceMode = false;
}

async function handleChatResponse(userInput) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    });

    const reader = response.body.getReader();
    let aiFullResponse = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = new TextDecoder().decode(value);
        aiFullResponse += chunk;
        updateChatUI(chunk); // Show text on screen as it arrives
    }

    // THE MAGIC PART: Only speak if the user used the mic
    if (isVoiceMode) {
        const utterance = new SpeechSynthesisUtterance(aiFullResponse);
        window.speechSynthesis.speak(utterance);
    } 
    // If isVoiceMode is false (typing), the code does nothing here, staying silent.
}
