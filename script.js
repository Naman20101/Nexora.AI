const apps = [
  // India
  { name: "Paytm", logo: "images/paytm.png", link: "https://paytm.com" },
  { name: "PhonePe", logo: "images/phonepe.png", link: "https://www.phonepe.com/" },
  { name: "Google Pay", logo: "images/googlepay.png", link: "https://pay.google.com/" },
  { name: "Amazon Pay", logo: "images/amazonpay.png", link: "https://pay.amazon.in" },
  { name: "BHIM", logo: "images/bhim.png", link: "https://www.bhimupi.org.in/" },
  { name: "MobiKwik", logo: "images/mobikwik.png", link: "https://www.mobikwik.com/" },
  { name: "Freecharge", logo: "images/freecharge.png", link: "https://www.freecharge.in/" },

  // USA
  { name: "PayPal", logo: "images/paypal.png", link: "https://www.paypal.com" },
  { name: "Venmo", logo: "images/venmo.png", link: "https://venmo.com" },
  { name: "Apple Pay", logo: "images/applepay.png", link: "https://www.apple.com/apple-pay/" },
  { name: "Cash App", logo: "images/cashapp.png", link: "https://cash.app/" },
  { name: "Zelle", logo: "images/zelle.png", link: "https://www.zellepay.com/" },

  // UK
  { name: "Revolut", logo: "images/revolut.png", link: "https://www.revolut.com/" },
  { name: "Monzo", logo: "images/monzo.png", link: "https://monzo.com/" },
  { name: "Pingit", logo: "images/pingit.png", link: "https://www.barclays.co.uk/" },

  // Australia
  { name: "Beem It", logo: "images/beemit.png", link: "https://www.beemit.com.au/" },
  { name: "Osko", logo: "images/osko.png", link: "https://payid.com.au/osko" },
  { name: "CommBank", logo: "images/commbank.png", link: "https://www.commbank.com.au/" },

  // China
  { name: "Alipay", logo: "images/alipay.png", link: "https://intl.alipay.com/" },
  { name: "WeChat Pay", logo: "images/wechat.png", link: "https://pay.weixin.qq.com/index.php/public/wechatpay" },
  { name: "UnionPay", logo: "images/unionpay.png", link: "https://www.unionpayintl.com/" },

  // Global
  { name: "Stripe", logo: "images/stripe.png", link: "https://stripe.com/" },
  { name: "Skrill", logo: "images/skrill.png", link: "https://www.skrill.com/" },
  { name: "Wise", logo: "images/wise.png", link: "https://wise.com/" },
  { name: "Neteller", logo: "images/neteller.png", link: "https://www.neteller.com/" },
];

const input = document.getElementById("searchInput");
const results = document.getElementById("results");
const suggestions = document.getElementById("suggestions");

let history = [];

input.addEventListener("input", () => {
  const keyword = input.value.toLowerCase();
  results.innerHTML = "";
  suggestions.innerHTML = "";

  if (!keyword) return;

  const filtered = apps.filter(app =>
    app.name.toLowerCase().includes(keyword)
  );

  if (filtered.length === 0) {
    suggestions.innerText = "No matching apps found.";
    return;
  }

  filtered.forEach(app => {
    const card = document.createElement("div");
    card.className = "result-item";
    card.innerHTML = `
      <a href="${app.link}" target="_blank">
        <img src="${app.logo}" alt="${app.name}"/>
        <p>${app.name}</p>
      </a>
    `;
    results.appendChild(card);
  });

  // Suggestions below input
  filtered.forEach(app => {
    const span = document.createElement("span");
    span.innerText = app.name;
    span.style.cursor = "pointer";
    span.style.marginRight = "10px";
    span.onclick = () => {
      input.value = app.name;
      input.dispatchEvent(new Event("input"));
      if (!history.includes(app.name)) {
        history.push(app.name);
      }
    };
    suggestions.appendChild(span);
  });

  // Show previously used
  if (history.length > 0) {
    const prevHeader = document.createElement("p");
    prevHeader.innerText = "Previously Used:";
    prevHeader.style.marginTop = "30px";
    suggestions.appendChild(prevHeader);
    history.slice(-5).forEach(appName => {
      const oldApp = apps.find(a => a.name === appName);
      const card = document.createElement("div");
      card.className = "result-item";
      card.innerHTML = `
        <a href="${oldApp.link}" target="_blank">
          <img src="${oldApp.logo}" alt="${oldApp.name}"/>
          <p>${oldApp.name}</p>
        </a>
      `;
      results.appendChild(card);
    });
  }
});
async function checkForScam() {
  const input = document.getElementById("urlInput").value.trim();
  const resultBox = document.getElementById("urlResult");
  resultBox.innerHTML = "Checking... 🔍";

  try {
    const response = await fetch("http://localhost:8000/check-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: input }),
    });

    const result = await response.json();

    if (result.is_scam) {
      resultBox.innerHTML = `⚠️ <b>Warning:</b> This URL may be fraudulent!<br><br><pre>${JSON.stringify(result.flags_triggered, null, 2)}</pre>`;
      resultBox.style.color = "#ff4444";
    } else {
      resultBox.innerHTML = `✅ This URL looks safe.<br><br><pre>${JSON.stringify(result.flags_triggered, null, 2)}</pre>`;
      resultBox.style.color = "#00ff99";
    }
  } catch (err) {
    resultBox.innerHTML = "❌ Error checking the URL. Make sure your backend is running.";
    resultBox.style.color = "#ff9900";
  }
}
async function checkScam() {
  const input = document.getElementById('scamInput').value;
  const resultElement = document.getElementById('scamResult');

  if (!input.trim()) {
    resultElement.textContent = "Please paste a link or message to check.";
    resultElement.style.color = "orange";
    return;
  }

  try {'https://nexora-ai-a-al-f-d-s-advanced-ai-powered.onrender.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: input })
    });

    const data = await response.json();

    if (data.is_fraud) {
      resultElement.textContent = "⚠️ This seems to be a scam!";
      resultElement.style.color = "red";
    } else {
      resultElement.textContent = "✅ Safe! This doesn't appear to be a scam.";
      resultElement.style.color = "lightgreen";
    }
  } catch (err) {
    resultElement.textContent = "Error checking the link. Please try again.";
    resultElement.style.color = "orange";
    console.error(err);
  }
}