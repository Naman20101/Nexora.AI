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

document.getElementById("checkBtn").addEventListener("click", async () => {
  try {
    const url = document.getElementById("urlInput").value;
    const response = await postJSON("/check-url", { url });
    console.log("OK", response);
    alert(JSON.stringify(response));
  } catch (err) {
    console.error("Request failed", err);
    alert("Error: " + err.message);
  }
});
