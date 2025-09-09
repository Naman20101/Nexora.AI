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

    // URL Checker Section
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

    // Prediction Endpoint Section
    document.getElementById("predictBtn").addEventListener("click", async () => {
        try {
            const feature1 = parseFloat(document.getElementById("feature1Input").value);
            const feature2 = parseFloat(document.getElementById("feature2Input").value);
            const feature3 = parseFloat(document.getElementById("feature3Input").value);
            
            if (isNaN(feature1) || isNaN(feature2) || isNaN(feature3)) {
                alert("Please enter valid numbers for all features.");
                return;
            }

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

    // Search Functionality
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
        
        if (query.length < 2) {
            return;
        }

        const filteredApps = paymentApps.filter(app => 
            app.name.toLowerCase().includes(query) ||
            app.country.toLowerCase().includes(query)
        );

        if (filteredApps.length > 0) {
            filteredApps.forEach(app => {
                const appElement = document.createElement("div");
                appElement.classList.add("suggestion-item");
                appElement.innerHTML = `<strong>${app.name}</strong> - ${app.country} <a href="${app.website}" target="_blank">Visit Site</a>`;
                suggestionsDiv.appendChild(appElement);
            });
        } else {
            suggestionsDiv.innerHTML = "No apps found.";
        }
    });

    // NEW: Smooth scroll for animations
    const sections = document.querySelectorAll('main > section');
    sections.forEach(section => {
        section.classList.add('hidden');
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
            }
        });
    }, {
        rootMargin: '0px',
        threshold: 0.2
    });

    sections.forEach(section => {
        observer.observe(section);
    });
});
