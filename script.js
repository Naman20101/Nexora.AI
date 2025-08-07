const paymentApps = {
    "Paytm": { link: "https://paytm.com", logo: "images/paytm.png" },
    "Google Pay": { link: "https://pay.google.com", logo: "logos/googlepay.png" },
    "PhonePe": { link: "https://phonepe.com", logo: "logos/phonepe.png" },
    "BHIM": { link: "https://bhimupi.org.in", logo: "logos/bhim.png" },
    "MobiKwik": { link: "https://mobikwik.com", logo: "logos/mobikwik.png" },
    "Freecharge": { link: "https://www.freecharge.in", logo: "logos/freecharge.png" },
    "Amazon Pay": { link: "https://pay.amazon.in", logo: "logos/amazonpay.png" },
    "PayPal": { link: "https://paypal.com", logo: "logos/paypal.png" },
    "Venmo": { link: "https://venmo.com", logo: "logos/venmo.png" },
    "Apple Pay": { link: "https://www.apple.com/apple-pay/", logo: "logos/applepay.png" },
    "Cash App": { link: "https://cash.app", logo: "logos/cashapp.png" },
    "Zelle": { link: "https://www.zellepay.com", logo: "logos/zelle.png" },
    "Revolut": { link: "https://revolut.com", logo: "logos/revolut.png" },
    "Monzo": { link: "https://monzo.com", logo: "logos/monzo.png" },
    "Barclays Pingit": { link: "https://www.pingit.com", logo: "logos/pingit.png" },
    "Beem It": { link: "https://www.beemit.com.au", logo: "logos/beemit.png" },
    "Osko": { link: "https://www.osko.com.au", logo: "logos/osko.png" },
    "CommBank app": { link: "https://www.commbank.com.au", logo: "logos/commbank.png" },
    "NAB Pay": { link: "https://www.nab.com.au", logo: "logos/nabpay.png" },
    "ANZ Pay": { link: "https://www.anz.com.au", logo: "logos/anzpay.png" },
    "Alipay": { link: "https://intl.alipay.com", logo: "logos/alipay.png" },
    "WeChat Pay": { link: "https://pay.weixin.qq.com", logo: "logos/wechatpay.png" },
    "UnionPay": { link: "https://www.unionpayintl.com", logo: "logos/unionpay.png" },
    "JD Pay": { link: "https://www.jd.id", logo: "logos/jdpay.png" },
    "Tenpay": { link: "https://www.tenpay.com", logo: "logos/tenpay.png" },
    "Stripe": { link: "https://stripe.com", logo: "logos/stripe.png" },
    "Skrill": { link: "https://www.skrill.com", logo: "logos/skrill.png" },
    "Wise": { link: "https://wise.com", logo: "logos/wise.png" },
    "Neteller": { link: "https://www.neteller.com", logo: "logos/neteller.png" }
};

const searchInput = document.getElementById("searchInput");
const suggestions = document.getElementById("suggestions");
const appDetails = document.getElementById("appDetails");
const recentAppsList = document.getElementById("recentApps");
let recentApps = [];

searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();
    suggestions.innerHTML = "";

    if (query.length === 0) return;

    const matchedApps = Object.keys(paymentApps).filter(app =>
        app.toLowerCase().includes(query)
    );

    matchedApps.forEach(app => {
        const li = document.createElement("li");
        li.textContent = app;
        li.onclick = () => selectApp(app);
        suggestions.appendChild(li);
    });
});

function selectApp(appName) {
    const app = paymentApps[appName];
    appDetails.innerHTML = `
        <img src="${app.logo}" alt="${appName}" class="payment-logo">
        <h2>${appName}</h2>
        <a href="${app.link}" target="_blank">Visit ${appName}</a>
    `;

    if (!recentApps.includes(appName)) {
        recentApps.unshift(appName);
        if (recentApps.length > 5) recentApps.pop();
        renderRecentApps();
    }

    searchInput.value = "";
    suggestions.innerHTML = "";
}

function renderRecentApps() {
    recentAppsList.innerHTML = "";
    recentApps.forEach(app => {
        const li = document.createElement("li");
        li.textContent = app;
        li.onclick = () => selectApp(app);
        recentAppsList.appendChild(li);
    });
}

