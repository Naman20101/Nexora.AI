document.addEventListener("DOMContentLoaded", () => {
    const BACKEND = "https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com";

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

    // This section is for the URL checker (the one that is already working)
    document.getElementById("checkBtn").addEventListener("click", async () => {
        try {
            const url = document.getElementById("urlInput").value;
            const response = await postJSON("/check-url", { url });
            console.log("OK", response);
            alert("URL Check: " + JSON.stringify(response));
        } catch (err) {
            console.error("Request failed", err);
            alert("Error: " + err.message);
        }
    });

    // New section for the /predict endpoint
    document.getElementById("predictBtn").addEventListener("click", async () => {
        try {
            // Get values from your new input fields
            const feature1 = parseFloat(document.getElementById("feature1Input").value);
            const feature2 = parseFloat(document.getElementById("feature2Input").value);
            const feature3 = parseFloat(document.getElementById("feature3Input").value);
            
            // Check if the values are valid numbers
            if (isNaN(feature1) || isNaN(feature2) || isNaN(feature3)) {
                alert("Please enter valid numbers for all features.");
                return;
            }

            // Send the data to the /predict endpoint
            const response = await postJSON("/predict", { 
                feature1: feature1,
                feature2: feature2,
                feature3: feature3
            });
            console.log("Prediction OK", response);
            alert("Prediction Result: " + JSON.stringify(response));

        } catch (err) {
            console.error("Prediction request failed", err);
            alert("Error: " + err.message);
        }
    });
});
