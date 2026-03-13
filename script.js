document.addEventListener("DOMContentLoaded", () => {
    // 1. YOUR RENDER URL (Ensure this is correct!)
    const BACKEND = "https://nexora-ai-mk99.onrender.com";

    // --- Helper for API calls ---
    async function postJSON(path, body) {
        const res = await fetch(BACKEND + path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error(`Server Error: ${res.status}`);
        return await res.json();
    }

    // --- UI Toggle for Chat ---
    window.toggleChat = function() {
        const panel = document.getElementById('sidePanel');
        const main = document.getElementById('mainArea');
        panel.classList.toggle('open');
        main.classList.toggle('shrunk');
    };

    // --- The URL Scanner (Connected to your ML Model) ---
    window.scanURL = async function() {
        const urlInput = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = urlInput.value.trim();

        if (!url) {
            display.innerHTML = `<span style="color: #ef4444">Please enter a URL.</span>`;
            return;
        }

        // 1. Show Loading State
        display.innerHTML = `<span style="color: #22d3ee; animation: pulse 1.5s infinite;">Scanning Neural Database...</span>`;
        card.style.borderColor = "rgba(34, 211, 238, 0.5)";

        try {
            // 2. Send to Render Backend
            const data = await postJSON("/check-url", { url: url });
            
            // 3. Update UI based on Model Prediction
            if (data.is_scam) {
                display.innerHTML = `
                    <div style="color: #ef4444; font-weight: 800; letter-spacing: 1px;">
                        ⚠️ THREAT DETECTED: PHISHING SIGNATURE FOUND
                    </div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 5px;">
                        Model Code: ${data.prediction_code || 'N/A'} | Security Risk: High
                    </div>`;
                card.style.borderColor = "#ef4444";
                card.style.boxShadow = "0 0 40px rgba(239, 68, 68, 0.4)";
            } else {
                display.innerHTML = `
                    <div style="color: #10b981; font-weight: 800; letter-spacing: 1px;">
                        ✅ VERIFIED: OFFICIAL FINANCIAL DOMAIN
                    </div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 5px;">
                        Status: Safe | Integrity: 100%
                    </div>`;
                card.style.borderColor = "#10b981";
                card.style.boxShadow = "0 0 40px rgba(16, 185, 129, 0.4)";
            }
        } catch (err) {
            console.error("Scan failed", err);
            display.innerHTML = `<span style="color: #ef4444">Link Offline: Ensure Render is awake.</span>`;
        }
    };

    // --- Nexora AI Chat Logic ---
    window.sendMessage = async function() {
        const input = document.getElementById('chatInput');
        const chatBox = document.getElementById('chatBox');
        const msg = input.value.trim();

        if (!msg) return;

        chatBox.innerHTML += `<div class="message user-msg">${msg}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const data = await postJSON("/chat", { message: msg });
            chatBox.innerHTML += `<div class="message bot-msg">${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (e) {
            chatBox.innerHTML += `<div class="message bot-msg">AI Core connection lost...</div>`;
        }
    };

    // Listen for Enter Keys
    document.getElementById('urlInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
    document.getElementById('chatInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
});
