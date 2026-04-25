document.addEventListener("DOMContentLoaded", () => {

    // ── 1. CONFIG ──────────────────────────────────────────────────────────────
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";
    const synth   = window.speechSynthesis;
    let shouldSpeakResponse = false;

    // ── 2. FORCE VISIBILITY ────────────────────────────────────────────────────
    document.querySelectorAll(".reveal").forEach(el => {
        el.style.opacity    = "1";
        el.style.transform  = "translateY(0)";
        el.classList.add("active");
    });
    const mainArea = document.getElementById("mainArea");
    if (mainArea) mainArea.style.display = "block";

    // ── 3. PANEL TOGGLE ────────────────────────────────────────────────────────
    window.toggleChat = () => {
        document.getElementById("sidePanel")?.classList.toggle("open");
    };

    // ── 4. TTS OUTPUT ──────────────────────────────────────────────────────────
    window.nexoraSpeak = function (text) {
        if (!shouldSpeakResponse || !text) return;
        synth.cancel();
        const utterance   = new SpeechSynthesisUtterance(text);
        utterance.rate    = 1.0;
        const voices      = synth.getVoices();
        utterance.voice   = voices.find(v => v.name.includes("Google UK English Male")) || voices[0] || null;
        synth.speak(utterance);
        shouldSpeakResponse = false;
    };

    // ── 5. VOICE INPUT (STT) ───────────────────────────────────────────────────
    window.startVoice = function () {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Voice input is not supported in your browser.");
            return;
        }

        const recognition = new SpeechRecognition();
        const micBtn      = document.getElementById("micBtn");

        recognition.lang         = "en-US";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            micBtn?.classList.add("listening");
            shouldSpeakResponse = true;
        };

        recognition.onend = () => {
            micBtn?.classList.remove("listening");  // ← was never removed before (bug fixed)
        };

        recognition.onerror = (event) => {
            micBtn?.classList.remove("listening");
            shouldSpeakResponse = false;
            console.error("Voice recognition error:", event.error);
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input      = document.getElementById("chatInput");
            if (input) {
                input.value = transcript;
                window.sendChatMessage(true);
            }
        };

        recognition.start();
    };

    // ── 6. CHAT ENGINE ─────────────────────────────────────────────────────────
    window.sendChatMessage = async function (isFromVoice = false) {
        const input  = document.getElementById("chatInput");
        const box    = document.getElementById("chatBox");
        if (!input || !box) return;

        const msg = input.value.trim();
        if (!msg) return;

        shouldSpeakResponse = isFromVoice;
        input.value = "";

        // ── User bubble (XSS-safe — NO innerHTML with user input) ──
        const userDiv  = document.createElement("div");
        userDiv.className = "user-msg";
        const userLabel   = document.createElement("b");
        userLabel.textContent = "You: ";
        const userText    = document.createTextNode(msg);   // safe — textContent only
        userDiv.appendChild(userLabel);
        userDiv.appendChild(userText);
        box.appendChild(userDiv);
        box.scrollTop = box.scrollHeight;

        // ── AI bubble ──
        const aiDiv       = document.createElement("div");
        aiDiv.className   = "ai-msg";
        const aiLabel     = document.createElement("b");
        aiLabel.textContent = "Nexora: ";
        const aiContent   = document.createElement("span");
        aiContent.className = "ai-content";
        aiContent.textContent = "...";
        aiDiv.appendChild(aiLabel);
        aiDiv.appendChild(aiContent);
        box.appendChild(aiDiv);
        box.scrollTop = box.scrollHeight;

        try {
            const response = await fetch(`${BACKEND}/chat`, {
                method:  "POST",
                headers: { "Content-Type": "application/json" },
                body:    JSON.stringify({ message: msg }),
            });

            if (!response.ok) {
                aiContent.textContent = `Error ${response.status}: Could not reach Nexora.`;
                return;
            }

            const reader  = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText  = "";
            aiContent.textContent = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                fullText   += chunk;
                aiContent.textContent = fullText;  // safe — textContent only
                box.scrollTop = box.scrollHeight;
            }

            window.nexoraSpeak(fullText);

        } catch (err) {
            aiContent.textContent = "Connection failed. Check your network or try again.";
            shouldSpeakResponse   = false;
            console.error("Chat error:", err);
        }
    };

    // ── 7. URL SCANNER ─────────────────────────────────────────────────────────
    window.scanURL = async function () {
        const urlIn   = document.getElementById("urlInput");
        const display = document.getElementById("result-display");
        if (!urlIn || !display) return;

        const url = urlIn.value.trim();
        if (!url) {
            display.textContent = "⚠️ Please enter a URL first.";
            return;
        }

        display.textContent = "⏳ INTERROGATING NEURAL CORE...";

        try {
            const res = await fetch(`${BACKEND}/check-url`, {
                method:  "POST",
                headers: { "Content-Type": "application/json" },
                body:    JSON.stringify({ url }),
            });

            if (!res.ok) {
                display.textContent = `⚠️ Scanner error: HTTP ${res.status}`;
                return;
            }

            const data = await res.json();
            display.textContent = data.is_scam
                ? `⚠️ ${data.message}`
                : `✅ ${data.message}`;

        } catch (e) {
            display.textContent = "🔴 Backend offline or unreachable.";
            console.error("Scan error:", e);
        }
    };

    // ── 8. PAYMENT APP SEARCH ──────────────────────────────────────────────────
    const PAYMENT_APPS = [
        { name: "PayPal",      region: "Global",  url: "https://paypal.com",     icon: "💳" },
        { name: "Paytm",       region: "India",   url: "https://paytm.com",      icon: "📱" },
        { name: "PhonePe",     region: "India",   url: "https://phonepe.com",    icon: "📲" },
        { name: "Google Pay",  region: "Global",  url: "https://pay.google.com", icon: "🔵" },
        { name: "Amazon Pay",  region: "Global",  url: "https://amazon.com/pay", icon: "🛒" },
        { name: "Apple Pay",   region: "Global",  url: "https://apple.com/pay",  icon: "🍎" },
        { name: "Venmo",       region: "US",      url: "https://venmo.com",      icon: "💸" },
        { name: "Cash App",    region: "US",      url: "https://cash.app",       icon: "💰" },
        { name: "Wise",        region: "Global",  url: "https://wise.com",       icon: "🌍" },
        { name: "Revolut",     region: "Global",  url: "https://revolut.com",    icon: "⚡" },
        { name: "Stripe",      region: "Global",  url: "https://stripe.com",     icon: "🔷" },
        { name: "Razorpay",    region: "India",   url: "https://razorpay.com",   icon: "⚙️" },
    ];

    window.searchApps = function () {
        const query       = document.getElementById("searchInput")?.value.toLowerCase().trim() || "";
        const suggestions = document.getElementById("suggestions");
        if (!suggestions) return;

        if (!query) {
            suggestions.innerHTML = "";
            return;
        }

        const matches = PAYMENT_APPS.filter(app =>
            app.name.toLowerCase().includes(query) || app.region.toLowerCase().includes(query)
        );

        if (matches.length === 0) {
            suggestions.innerHTML = `<div class="suggestion-item">No apps found for "${query}"</div>`;
            return;
        }

        suggestions.innerHTML = matches.map(app => `
            <div class="suggestion-item">
                <span>${app.icon} <strong>${app.name}</strong> — ${app.region}</span>
                <a href="${app.url}" target="_blank" rel="noopener noreferrer" class="verify-link">Verify ↗</a>
            </div>
        `).join("");
    };

    // ── 9. KEYBOARD SHORTCUTS ──────────────────────────────────────────────────
    document.getElementById("chatInput")?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            shouldSpeakResponse = false;
            window.sendChatMessage(false);
        }
    });

    document.getElementById("urlInput")?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") window.scanURL();
    });

});
