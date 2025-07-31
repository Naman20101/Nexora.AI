document.getElementById("fraudForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = {};

  for (let [key, value] of formData.entries()) {
    data[key] = parseFloat(value);
  }

  try {
    const response = await fetch("https://your-backend.onrender.com/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    document.getElementById("result").innerText =
      `Prediction: ${result.prediction === 1 ? "⚠️ Fraud Detected" : "✅ Transaction Safe"}`;
  } catch (err) {
    console.error("Error:", err);
    document.getElementById("result").innerText = "Error connecting to backend.";
  }
});
