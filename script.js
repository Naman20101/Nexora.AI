document.addEventListener("DOMContentLoaded", () => {
    // 1. CONFIGURATION
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    let lastScanData = null;

    console.log("Nexora AI: Neural Core Synced");

    // --- 2. HIGH-END SCROLL REVEAL (Intersection Observer) ---
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
        // Only shrink main area on large screens to prevent mobile glitches
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

        // Pulse Animation
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

    // --- 5. AI ASSISTANT LOGIC ---
    window.sendChatMessage = async function() {
        const input = document.getElementById('chatInput');
        const box = document.getElementById('chatBox');
        const msg = input.value.trim();
        
        if (!msg) return;

        // User Bubble
        box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
        input.value = '';
        box.scrollTop = box.scrollHeight;

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });
            const data = await response.json();
            
            // AI Bubble
            box.innerHTML += `<div class="ai-msg"><b>Nexora:</b> ${data.response}</div>`;
        } catch (err) {
            box.innerHTML += `<div style="color:var(--danger); font-size:0.7rem; padding:10px;">Link Severed. AI is offline.</div>`;
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

    // App Search Logic
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
            div.className = "suggestion-item reveal active"; // Force active for instant search results
            div.innerHTML = `<span>${app.name}</span> <a href="${app.website}" target="_blank">OFFICIAL</a>`;
            suggestions.appendChild(div);
        });
    });

    // Listeners
    document.getElementById('urlInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') scanURL(); });
    document.getElementById('chatInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChatMessage(); });
});
