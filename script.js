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
    // Initial loading state
    aiDiv.innerHTML = `<b>Nexora:</b> <span class="ai-content">...</span>`;
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

            // SPEED FIX: Clear "..." immediately when data starts flowing
            if (firstChunk) {
                contentSpan.innerText = "";
                firstChunk = false;
            }

            fullText += decoder.decode(value, { stream: true });
            contentSpan.innerText = fullText;
            
            // Optimization: Only scroll if the user isn't manually scrolling up
            box.scrollTop = box.scrollHeight;
        }
        window.nexoraSpeak(fullText);
    } catch (err) {
        aiDiv.querySelector('.ai-content').innerText = "Neural Link timed out. Try again.";
    }
};
// Add this at the bottom of your DOMContentLoaded listener
fetch(`${BACKEND}/check-url`, { 
    method: "POST", 
    body: JSON.stringify({url: "ping.com"}) 
}).then(() => console.log("Backend Warmed Up"));
