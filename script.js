const apps = [
  // India
  { name: "Paytm", url: "https://paytm.com", logo: "paytm.png" },
  { name: "Google Pay", url: "https://pay.google.com", logo: "gpay.png" },
  { name: "PhonePe", url: "https://www.phonepe.com", logo: "phonepe.png" },
  { name: "BHIM", url: "https://www.bhimupi.org.in/", logo: "bhim.png" },
  { name: "MobiKwik", url: "https://www.mobikwik.com", logo: "mobikwik.png" },
  { name: "Freecharge", url: "https://www.freecharge.in", logo: "freecharge.png" },
  { name: "Amazon Pay", url: "https://www.amazon.in/amazonpay", logo: "amazonpay.png" },

  // USA
  { name: "PayPal", url: "https://www.paypal.com", logo: "paypal.png" },
  { name: "Venmo", url: "https://venmo.com", logo: "venmo.png" },
  { name: "Apple Pay", url: "https://www.apple.com/apple-pay/", logo: "applepay.png" },
  { name: "Cash App", url: "https://cash.app", logo: "cashapp.png" },
  { name: "Zelle", url: "https://www.zellepay.com/", logo: "zelle.png" },

  // UK
  { name: "Revolut", url: "https://www.revolut.com", logo: "revolut.png" },
  { name: "Monzo", url: "https://monzo.com", logo: "monzo.png" },
  { name: "Barclays Pingit", url: "#", logo: "pingit.png" },

  // Australia
  { name: "Beem It", url: "https://www.beemit.com.au", logo: "beemit.png" },
  { name: "Osko", url: "https://www.osko.com.au", logo: "osko.png" },
  { name: "CommBank", url: "https://www.commbank.com.au", logo: "commbank.png" },
  { name: "NAB Pay", url: "#", logo: "nabpay.png" },
  { name: "ANZ Pay", url: "#", logo: "anzpay.png" },

  // China
  { name: "Alipay", url: "https://intl.alipay.com", logo: "alipay.png" },
  { name: "WeChat Pay", url: "https://pay.weixin.qq.com", logo: "wechatpay.png" },
  { name: "UnionPay", url: "https://www.unionpayintl.com", logo: "unionpay.png" },
  { name: "JD Pay", url: "#", logo: "jdpay.png" },
  { name: "Tenpay", url: "#", logo: "tenpay.png" },

  // International
  { name: "Stripe", url: "https://stripe.com", logo: "stripe.png" },
  { name: "Skrill", url: "https://www.skrill.com", logo: "skrill.png" },
  { name: "Wise", url: "https://wise.com", logo: "wise.png" },
  { name: "Neteller", url: "https://www.neteller.com", logo: "neteller.png" }
];

// Generate Cards
const container = document.getElementById("appsContainer");
apps.forEach(app => {
  const card = document.createElement("div");
  card.className = "app-card";
  card.innerHTML = `
    <a href="${app.url}" target="_blank">
      <img class="app-logo" src="images/${app.logo}" alt="${app.name}" />
      <div>${app.name}</div>
    </a>
  `;
  container.appendChild(card);
});

// Filter/Search Logic
document.getElementById("searchInput").addEventListener("input", function () {
  const query = this.value.toLowerCase();
  const cards = document.querySelectorAll(".app-card");
  cards.forEach(card => {
    const appName = card.textContent.toLowerCase();
    card.style.display = appName.includes(query) ? "block" : "none";
  });
});

