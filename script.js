const form = document.getElementById("prediction-form");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  const inputData = Object.fromEntries(formData.entries());

  for (let key in inputData) {
    inputData[key] = parseFloat(inputData[key]);
  }

  try {
    const res = await fetch("https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(inputData)
    });

    const data = await res.json();
    resultDiv.innerText = `Prediction: ${data.prediction}`;
  } catch (err) {
    resultDiv.innerText = "Error contacting backend.";
    console.error(err);
  }
});
