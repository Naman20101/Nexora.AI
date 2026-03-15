window.scanURL = async function() {
    const urlIn = document.getElementById('urlInput');
    const display = document.getElementById('result-display');
    if (!urlIn || !display) return;
    
    // ADDED: Loading Spinner
    display.innerHTML = `<div class="spinner"></div> ANALYZING DNA...`;

    try {
        const res = await fetch(`${BACKEND}/check-url`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: urlIn.value })
        });
        const data = await res.json();
        display.innerHTML = data.is_scam ? `⚠️ ${data.message}` : `✅ SECURE`;
    } catch (e) { 
        display.innerHTML = "OFFLINE: Wake up Backend"; 
    }
};

// Chat Speed Fix with First-Chunk Logic
window.sendChatMessage = async function(isFromVoice = false) {
    const input = document.getElementById('chatInput');
    const box = document.getElementById('chatBox');
    if (!input || !box || !input.value.trim()) return;

    const msg = input.value;
    box.innerHTML += `<div class="user-msg"><b>You:</b> ${msg}</div>`;
    input.value = '';

    const aiDiv = document.createElement('div');
    aiDiv.className = 'ai-msg';
    aiDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content"><div class="spinner"></div></span>`;
    box.appendChild(aiDiv);
    box.scrollTop = box.scrollHeight;

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
        if (firstChunk) { contentSpan.innerHTML = ""; firstChunk = false; }
        fullText += decoder.decode(value, { stream: true });
        contentSpan.innerText = fullText;
        box.scrollTop = box.scrollHeight;
    }
    if (isFromVoice) window.nexoraSpeak(fullText);
};
