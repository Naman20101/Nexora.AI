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
document.addEventListener("DOMContentLoaded", () => {
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    let lastScanData = null; // Store for report

    window.scanURL = async function() {
        const input = document.getElementById('urlInput');
        const display = document.getElementById('result-display');
        const card = document.getElementById('scannerCard');
        const url = input.value.trim();

        if (url.length < 4) {
            display.innerHTML = "Input too short to analyze.";
            return;
        }

        display.innerHTML = `<span class="loading-text">NEURAL ANALYSIS IN PROGRESS...</span>`;

        try {
            const response = await fetch(`${BACKEND}/check-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });
            const data = await response.json();
            lastScanData = data; // Save data for report

            if (data.is_scam) {
                display.innerHTML = `<div style="color:#ef4444">⚠️ ${data.message}</div>`;
                card.className = "scanner-card danger-glow";
            } else {
                display.innerHTML = `<div style="color:#10b981">✅ ${data.message}</div>`;
                card.className = "scanner-card success-glow";
            }

            // Show Download Button
            display.innerHTML += `<br><button onclick="downloadReport()" class="report-btn">Download PDF Report</button>`;

        } catch (err) {
            display.innerHTML = "System Timeout. Try again.";
        }
    };

    window.downloadReport = function() {
        if (!lastScanData) return;
        
        const reportContent = `
            NEXORA.AI SECURITY AUDIT
            ------------------------
            URL: ${lastScanData.url}
            RESULT: ${lastScanData.is_scam ? "MALICIOUS" : "SAFE"}
            THREAT CODE: ${lastScanData.prediction_code}
            TIMESTAMP: ${new Date().toLocaleString()}
            
            TECHNICAL DETAILS:
            - Length: ${lastScanData.details?.url_length}
            - Special Chars: ${lastScanData.details?.num_special_chars}
            - Digits: ${lastScanData.details?.num_digits}
            
            This report is generated by Nexora Neural Engine.
        `;
        
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const element = document.createElement('a');
        element.href = URL.createObjectURL(blob);
        element.download = "Nexora_Scan_Report.txt";
        document.body.appendChild(element);
        element.click();
    };
});

// --- AI ASSISTANT LOGIC ---
window.sendChatMessage = async function() {
    const input = document.getElementById('chatInput');
    const box = document.getElementById('chatBox');
    const msg = input.value.trim();
    
    if (!msg) return;

    // Add User Bubble
    box.innerHTML += `
        <div style="text-align: right; margin-bottom: 10px;">
            <span style="background: rgba(0, 242, 254, 0.2); padding: 8px 12px; border-radius: 12px; display: inline-block;">
                ${msg}
            </span>
        </div>`;
    
    input.value = '';
    box.scrollTop = box.scrollHeight;

    try {
        const response = await fetch(`${BACKEND}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        
        // Add AI Bubble
        box.innerHTML += `
            <div style="text-align: left; margin-bottom: 10px; animation: fadeIn 0.5s;">
                <span style="background: rgba(255, 255, 255, 0.1); padding: 8px 12px; border-radius: 12px; display: inline-block; border-left: 2px solid #00f2fe;">
                    <b>Nexora:</b> ${data.response}
                </span>
            </div>`;
    } catch (err) {
        box.innerHTML += `<div style="color: #64748b; font-size: 0.8rem;">Assistant sync error. Check backend.</div>`;
    }
    box.scrollTop = box.scrollHeight;
};

// Allow "Enter" key to send chat messages
document.getElementById('chatInput')?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendChatMessage();
});

// --- UI TRANSITIONS ---
// This adds a subtle "scanning" pulse to the card when you click the button
const originalScan = window.scanURL;
window.scanURL = async function() {
    const card = document.getElementById('scannerCard');
    card.style.transform = "scale(0.98)";
    setTimeout(() => card.style.transform = "scale(1)", 150);
    
    // Call the original scan function
    await originalScan();
};
// 1. SCROLL REVEAL LOGIC
function reveal() {
    var reveals = document.querySelectorAll(".reveal");
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 150;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
    }
}
window.addEventListener("scroll", reveal);

// 2. UPDATED CHAT (Visible Text Fix)
window.sendChatMessage = async function() {
    const input = document.getElementById('chatInput');
    const box = document.getElementById('chatBox');
    const msg = input.value.trim();
    if (!msg) return;

    box.innerHTML += `<div class="user-msg" style="color:white; margin-bottom:10px;"><b>User:</b> ${msg}</div>`;
    input.value = '';

    try {
        const response = await fetch(`${BACKEND}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        box.innerHTML += `<div class="ai-msg" style="color:#22d3ee; margin-bottom:10px;"><b>Assistant:</b> ${data.response}</div>`;
    } catch (err) {
        box.innerHTML += `<div style="color:red">Connection Error.</div>`;
    }
    box.scrollTop = box.scrollHeight;
};
