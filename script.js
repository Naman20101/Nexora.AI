const paymentApps = [
  { name: "Paytm", file: "paytm.png", url: "https://paytm.com" },
  { name: "PhonePe", file: "phonepe.png", url: "https://www.phonepe.com/" },
  { name: "Google Pay", file: "gpay.png", url: "https://pay.google.com/" },
  { name: "PayPal", file: "paypal.png", url: "https://www.paypal.com" },
  { name: "Venmo", file: "venmo.png", url: "https://venmo.com" },
  { name: "Apple Pay", file: "applepay.png", url: "https://www.apple.com/apple-pay/" },
  { name: "BHIM", file: "bhim.png", url: "https://www.bhimupi.org.in/" },
  { name: "MobiKwik", file: "mobikwik.png", url: "https://www.mobikwik.com/" },
  { name: "Freecharge", file: "freecharge.png", url: "https://www.freecharge.in/" },
  { name: "Amazon Pay", file: "amazonpay.png", url: "https://www.amazon.in/amazonpay" },
  { name: "Cash App", file: "cashapp.png", url: "https://cash.app/" },
  { name: "Zelle", file: "zelle.png", url: "https://www.zellepay.com/" },
  { name: "Revolut", file: "revolut.png", url: "https://www.revolut.com/" },
  { name: "Monzo", file: "monzo.png", url: "https://monzo.com/" },
  { name: "Pingit", file: "pingit.png", url: "https://www.barclays.co.uk/ways-to-bank/pingit/" },
  { name: "Beem It", file: "beemit.png", url: "https://www.beemit.com.au/" },
  { name: "Osko", file: "osko.png", url: "https://www.osko.com.au/" },
  { name: "CommBank", file: "commbank.png", url: "https://www.commbank.com.au/digital-banking.html" },
  { name: "NAB Pay", file: "nabpay.png", url: "https://www.nab.com.au/" },
  { name: "ANZ Pay", file: "anzpay.png", url: "https://www.anz.com.au/personal/ways-bank/payments/anz-pay/" },
  { name: "Alipay", file: "alipay.png", url: "https://intl.alipay.com/" },
  { name: "WeChat Pay", file: "wechatpay.png", url: "https://pay.weixin.qq.com/" },
  { name: "UnionPay", file: "unionpay.png", url: "https://www.unionpayintl.com/" },
  { name: "JD Pay", file: "jdpay.png", url: "https://www.jdpay.com/" },
  { name: "Tenpay", file: "tenpay.png", url: "https://www.tenpay.com/" },
  { name: "Stripe", file: "stripe.png", url: "https://stripe.com/" },
  { name: "Skrill", file: "skrill.png", url: "https://www.skrill.com/" },
  { name: "Wise", file: "wise.png", url: "https://wise.com/" },
  { name: "Neteller", file: "neteller.png", url: "https://www.neteller.com/" },
];

const searchInput = document.getElementById("searchInput");
const resultsDiv = document.getElementById("results");
const suggestionsBox = document.getElementById("suggestions");

searchInput.addEventListener("input", function () {
  const query = this.value.toLowerCase();
  const filtered = paymentApps.filter(app =>
    app.name.toLowerCase().includes(query)
  );

  suggestionsBox.innerHTML = "";
  resultsDiv.innerHTML = "";

  if (query) {
    filtered.forEach(app => {
      const div = document.createElement("div");
      div.textContent = app.name;
      div.onclick = () => {
        showResults(app.name);
        searchInput.value = app.name;
        suggestionsBox.innerHTML = "";
      };
      suggestionsBox.appendChild(div);
    });
  }
});

function showResults(name) {
  const app = paymentApps.find(app => app.name.toLowerCase() === name.toLowerCase());
  resultsDiv.innerHTML = "";

  if (app) {
    const a = document.createElement("a");
    a.href = app.url;
    a.target = "_blank";

    const img = document.createElement("img");
    img.src = `images/${app.file}`;
    img.alt = app.name;

    a.appendChild(img);
    resultsDiv.appendChild(a);
  }
}
