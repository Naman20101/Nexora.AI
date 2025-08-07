const apps = [
  {
    name: "Paytm",
    keywords: ["india", "pay", "wallet"],
    image: "images/paytm.png",
    link: "https://paytm.com"
  },
  {
    name: "PhonePe",
    keywords: ["india", "phone", "upi"],
    image: "images/phonepe.png",
    link: "https://www.phonepe.com"
  },
  {
    name: "Google Pay",
    keywords: ["gpay", "upi", "google", "pay"],
    image: "images/gpay.png",
    link: "https://pay.google.com"
  },
  {
    name: "PayPal",
    keywords: ["paypal", "usa", "international", "wallet"],
    image: "images/paypal.png",
    link: "https://www.paypal.com"
  },
  // Add more apps below as we proceed
];

let recentSearches = [];

const input = document.getElementById("searchInput");
const resultDiv = document.getElementById("result");
const suggestionsDiv = document.getElementById("suggestions");

input.addEventListener("input", () => {
  const value = input.value.toLowerCase();
  const matchedApps = apps.filter(app =>
    app.name.toLowerCase().includes(value) ||
    app.keywords.some(k => k.includes(value))
  );

  suggestionsDiv.innerHTML = matchedApps
    .map(app => `<div onclick="showApp('${app.name}')">${app.name}</div>`)
    .join("");

  if (!value) {
    suggestionsDiv.innerHTML = "";
  }
});

function showApp(appName) {
  const app = apps.find(a => a.name === appName);
  if (!app) return;

  resultDiv.innerHTML = `
    <h2>${app.name}</h2>
    <img src="${app.image}" alt="${app.name} logo" />
    <br />
    <a href="${app.link}" target="_blank">Visit ${app.name}</a>
  `;

  if (!recentSearches.includes(app.name)) {
    recentSearches.push(app.name);
  }

  suggestionsDiv.innerHTML = `<small>Previously Searched: ${recentSearches.join(", ")}</small>`;
}

