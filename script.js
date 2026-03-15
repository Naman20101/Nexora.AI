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
    
    // NEW: Added the round spinner symbol here
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

            // SPEED FIX: Remove spinner/dots immediately when the first letter arrives
            if (firstChunk) {
                contentSpan.innerHTML = ""; // Use innerHTML to clear the spinner div
                firstChunk = false;
            }

            fullText += decoder.decode(value, { stream: true });
            contentSpan.innerText = fullText;
            box.scrollTop = box.scrollHeight;
        }
        
        if (shouldSpeakResponse) {
            window.nexoraSpeak(fullText);
        }
    } catch (err) {
        contentSpan.innerText = "Neural Link timed out. Try again.";
    }
};

// IMPROVED PING: Added headers to ensure the backend accepts the warm-up call
fetch(`${BACKEND}/check-url`, { 
    method: "POST", 
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({url: "ping.com"}) 
}).then(() => console.log("Backend Warmed Up")).catch(e => console.log("Warm-up pending..."));
