function simulateTransaction(appName) {
  alert("Initiating fraud detection on " + appName + " transaction...");
  // You can trigger an API call here later if needed
}
function filterApps() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const icons = document.querySelectorAll("#paymentOptions a");

  icons.forEach(icon => {
    const name = icon.getAttribute("data-name");
    if (name.includes(input)) {
      icon.style.display = "inline-block";
    } else {
      icon.style.display = "none";
    }
  });
}
