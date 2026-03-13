document.addEventListener("DOMContentLoaded", () => {
    // 1. YOUR LIVE RENDER URL (Updated from your logs)
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";

    console.log("Nexora AI Hub: Connection Initialized");

    // --- UI Toggles ---
    window.toggleChat = () => {
        document.getElementById('sidePanel').classList.toggle('open');
        document.getElementById('mainArea').classList.toggle('shrunk');
    };

    // --- Neural URL Scanner ---
    window.scanURL = async function() {
        const input = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = input.value.trim();

        if (!url) {
            display.innerHTML = `<span style="color: #ef4444">Input required for scan.</span>`;
            return;
        }

        // Visual feedback for scanning
        display.innerHTML = `<span class="loading-text">INTERROGATING NEURAL DATABASE...</span>`;
        card.style.borderColor = "var(--accent-cyan)";

        try {
            const response = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) throw new Error("Backend Offline");

            const data = await response.json();
            
            if (data.is_scam) {
                display.innerHTML = `
                    <div style="color: #ef4444; font-weight: 800; letter-spacing: 1px;">⚠️ THREAT DETECTED</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 5px;">VERDICT: ${data.message} | CODE: ${data.prediction_code}</div>`;
                card.classList.add('danger-glow');
                card.classList.remove('success-glow');
            } else {
                display.innerHTML = `
                    <div style="color: #10b981; font-weight: 800; letter-spacing: 1px;">✅ SAFE DOMAIN</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 5px;">VERDICT: ${data.message} | INTEGRITY: 100%</div>`;
                card.classList.add('success-glow');
                card.classList.remove('danger-glow');
            }
        } catch (err) {
            console.error("Scan Error:", err);
            display.innerHTML = `<span style="color: #ef4444">Link Error: Backend wake-up required.</span>`;
        }
    };

    // --- Payment App Search ---
    const apps = [
        { name: "Paytm", country: "India", website: "https://paytm.com" },
        { name: "PayPal", country: "Global", website: "https://paypal.com" },
        { name: "Venmo", country: "USA", website: "https://venmo.com" },
        { name: "PhonePe", country: "India", website: "https://phonepe.com" },
        { name: "Google Pay", country: "Global", website: "https://pay.google.com" },
        { name: "Cash App", country: "USA", website: "https://cash.app" },
        { name: "Revolut", country: "Europe", website: "https://revolut.com" }
    ];

    document.getElementById("searchInput").addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const suggestions = document.getElementById("suggestions");
        suggestions.innerHTML = "";
        
        if (query.length < 2) return;

        const results = apps.filter(a => a.name.toLowerCase().includes(query) || a.country.toLowerCase().includes(query));

        if (results.length > 0) {
            results.forEach(app => {
                const div = document.createElement("div");
                div.className = "suggestion-item";
                div.innerHTML = `
                    <span><strong>${app.name}</strong> <small style="color:#64748b">(${app.country})</small></span>
                    <a href="${app.website}" target="_blank">OFFICIAL SITE</a>`;
                suggestions.appendChild(div);
            });
        } else {
            suggestions.innerHTML = `<div style="padding:15px; color:#475569">No verified apps found.</div>`;
        }
    });

    // --- AI Chat Messenger ---
    window.sendMessage = async function() {
        const input = document.getElementById('chatInput');
        const chatBox = document.getElementById('chatBox');
        const text = input.value.trim();

        if (!text) return;

        chatBox.innerHTML += `<div class="message user-msg">${text}</div>`;
        input.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const res = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            chatBox.innerHTML += `<div class="message bot-msg">${data.response}</div>`;
        } catch (e) {
            chatBox.innerHTML += `<div class="message bot-msg">Communication link severed... AI Offline.</div>`;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Keyboard support
    document.getElementById('urlInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
    document.getElementById('chatInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
});
