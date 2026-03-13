document.addEventListener("DOMContentLoaded", () => {
    // 1. Backend Configuration
    const BACKEND = "https://nexora-ai-mk99.onrender.com";

    // --- Helper for API calls ---
    async function postJSON(path, body) {
        const res = await fetch(BACKEND + path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
        if (!res.ok) {
            let errBody;
            try { errBody = await res.json(); } catch (e) { errBody = await res.text(); }
            throw new Error(`Status ${res.status}: ${JSON.stringify(errBody)}`);
        }
        return await res.json();
    }

    // --- 2. UI Toggles & Transitions ---
    window.toggleChat = function() {
        const panel = document.getElementById('sidePanel');
        const main = document.getElementById('mainArea');
        panel.classList.toggle('open');
        main.classList.toggle('shrunk');
    };

    // --- 3. Neural URL Scanner ---
    window.scanURL = async function() {
        const urlInput = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = urlInput.value.trim();

        if (!url) {
            display.innerHTML = `<span style="color: #ef4444">Please enter a URL first.</span>`;
            return;
        }

        display.innerHTML = `<span style="color: #22d3ee">Analyzing neural patterns...</span>`;
        card.style.borderColor = "rgba(34, 211, 238, 0.5)";

        try {
            const data = await postJSON("/check-url", { url });
            
            if (data.is_scam) {
                display.innerHTML = `<span style="color: #ef4444; font-weight: 800;">⚠️ THREAT DETECTED: SUSPICIOUS URL</span>`;
                card.style.borderColor = "#ef4444";
                card.style.boxShadow = "0 0 40px rgba(239, 68, 68, 0.3)";
            } else {
                display.innerHTML = `<span style="color: #10b981; font-weight: 800;">✅ CLEAR: OFFICIAL/SAFE DOMAIN</span>`;
                card.style.borderColor = "#10b981";
                card.style.boxShadow = "0 0 40px rgba(16, 185, 129, 0.3)";
            }
        } catch (err) {
            console.error("Scan failed", err);
            display.innerHTML = `<span style="color: #ef4444">Error: Connection to Neural Link lost.</span>`;
        }
    };

    // --- 4. Nexora AI Chat Logic ---
    window.sendMessage = async function() {
        const input = document.getElementById('chatInput');
        const chatBox = document.getElementById('chatBox');
        const msg = input.value.trim();

        if (!msg) return;

        // Display User Message
        chatBox.innerHTML += `<div class="message user-msg">${msg}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const data = await postJSON("/chat", { message: msg });
            
            // Display AI Response
            chatBox.innerHTML += `<div class="message bot-msg">${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (e) {
            chatBox.innerHTML += `<div class="message bot-msg">System error: Unable to reach AI core.</div>`;
        }
    };

    // --- 5. Payment App Search Logic ---
    const paymentApps = [
        { name: "Paytm", country: "India", website: "https://paytm.com" },
        { name: "PhonePe", country: "India", website: "https://www.phonepe.com" },
        { name: "Google Pay", country: "Global", website: "https://pay.google.com" },
        { name: "PayPal", country: "Global", website: "https://www.paypal.com" },
        { name: "Alipay", country: "China", website: "https://www.alipay.com" },
        { name: "WeChat Pay", country: "China", website: "https://pay.weixin.qq.com" },
        { name: "Venmo", country: "USA", website: "https://venmo.com" },
        { name: "Cash App", country: "USA", website: "https://cash.app" },
        { name: "Zelle", country: "USA", website: "https://www.zellepay.com" },
        { name: "Revolut", country: "Europe", website: "https://www.revolut.com" },
        { name: "Pix", country: "Brazil", website: "https://www.bcb.gov.br/estabilidadefinanceira/pix" },
    ];

    const searchInput = document.getElementById("searchInput");
    const suggestionsDiv = document.getElementById("suggestions");

    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        suggestionsDiv.innerHTML = "";
        
        if (query.length < 2) return;

        const filteredApps = paymentApps.filter(app => 
            app.name.toLowerCase().includes(query) ||
            app.country.toLowerCase().includes(query)
        );

        if (filteredApps.length > 0) {
            filteredApps.forEach(app => {
                const appElement = document.createElement("div");
                appElement.classList.add("suggestion-item");
                appElement.innerHTML = `
                    <div style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); cursor: pointer;" 
                         onclick="window.open('${app.website}', '_blank')">
                        <strong style="color: #22d3ee">${app.name}</strong> 
                        <span style="font-size: 0.8rem; color: #94a3b8;">(${app.country})</span>
                    </div>`;
                suggestionsDiv.appendChild(appElement);
            });
        } else {
            suggestionsDiv.innerHTML = `<div style="padding: 10px; color: #64748b;">No matching apps found.</div>`;
        }
    });

    // --- 6. Event Listeners for Keyboard ---
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') scanURL();
    });

    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
