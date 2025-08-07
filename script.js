const paymentApps = [
  { name: "Paytm", logo: "paytm.png", link: "https://paytm.com" },
  { name: "PhonePe", logo: "phonepe.png", link: "https://www.phonepe.com" },
  { name: "Google Pay", logo: "gpay.png", link: "https://pay.google.com" },
  { name: "PayPal", logo: "paypal.png", link: "https://www.paypal.com" },
  { name: "Venmo", logo: "venmo.png", link: "https://venmo.com" },
  { name: "Apple Pay", logo: "applepay.png", link: "https://www.apple.com/apple-pay/" },
  { name: "Cash App", logo: "cashapp.png", link: "https://cash.app" },
  { name: "Zelle", logo: "zelle.png", link: "https://www.zellepay.com" },
  { name: "Revolut", logo: "revolut.png", link: "https://www.revolut.com" },
  { name: "Stripe", logo: "stripe.png", link: "https://stripe.com" },
  { name: "Wise", logo: "wise.png", link: "https://wise.com" },
  { name: "Alipay", logo: "alipay.png", link: "https://intl.alipay.com" },
  { name: "WeChat Pay", logo: "wechat.png", link: "https://pay.weixin.qq.com/index.php" },
  { name: "UnionPay", logo: "unionpay.png", link: "http://www.unionpayintl.com" },
  { name: "JD Pay", logo: "jdpay.png", link: "https://www.jdpay.com" },
  { name: "Tenpay", logo: "tenpay.png", link: "https://www.tenpay.com" },
  { name: "Skrill", logo: "skrill.png", link: "https://www.skrill.com" },
  { name: "Neteller", logo: "neteller.png", link: "https://www.neteller.com" }
];

const searchInput = document.getElementById("search");
const suggestionsBox = document.getElementById("suggestions");
const resultBox = document.getElementById("result");
const recentList = document.getElementById("recent-list");

let recentApps = [];

searchInput.addEventListener("input", function () {
  const query = this.value.toLowerCase();
  suggestionsBox.innerHTML = "";

  if (!query) return;

  const matches = paymentApps.filter(app =>
    app.name.toLowerCase().includes(query)
  );

  matches.forEach(app => {
    const div = document.createElement("div");
    div.textContent = app.name;
    div.onclick = () => showApp(app);
    suggestionsBox.appendChild(div);
  });
});

function showApp(app) {
  suggestionsBox.innerHTML = "";
  searchInput.value = "";

  const html = `
    <div class="app-card">
      <img src="images/${app.logo}" alt="${app.name}" />
      <h3>${app.name}</h3>
      <a href="${app.link}" target="_blank">Visit Website</a>
    </div>
  `;
  resultBox.innerHTML = html;

  // Save to recently used
  if (!recentApps.includes(app.name)) {
    recentApps.unshift(app.name);
    if (recentApps.length > 5) recentApps.pop();
    updateRecent();
  }
}

function updateRecent() {
  recentList.innerHTML = "";
  recentApps.forEach(appName => {
    const li = document.createElement("li");
    li.textContent = appName;
    li.onclick = () => {
      const app = paymentApps.find(a => a.name === appName);
      if (app) showApp(app);
    };
    recentList.appendChild(li);
  });
}
