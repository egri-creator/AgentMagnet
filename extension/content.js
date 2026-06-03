// AgentMagnet Chrome Extension — injected on Amazon & eBay product pages
// Shows price comparison, agent reviews, coupons, price rating

const AGENTMAGNET_API = "https://agentmagnet-y07b.onrender.com/api";

(function () {
  // Don't inject twice
  if (document.getElementById("agentmagnet-root")) return;

  // Detect product info from page
  function detectProduct() {
    const host = window.location.hostname;

    if (host.includes("amazon")) {
      return detectAmazonProduct();
    }
    if (host.includes("ebay")) {
      return detectEbayProduct();
    }
    return null;
  }

  function detectAmazonProduct() {
    const titleEl =
      document.getElementById("productTitle") ||
      document.querySelector("#title span");
    if (!titleEl) return null;

    const title = titleEl.innerText.trim();
    const priceEl =
      document.querySelector(".a-price .a-offscreen") ||
      document.querySelector("#priceblock_ourprice") ||
      document.querySelector("#priceblock_dealprice");
    const price = priceEl
      ? parseFloat(priceEl.innerText.replace(/[^0-9.]/g, ""))
      : 0;

    // Extract ASIN from URL
    const asinMatch = window.location.pathname.match(/\/(dp|product)\/([A-Z0-9]{10})/);
    const asin = asinMatch ? asinMatch[2] : null;

    // Detect category from breadcrumbs
    const breadcrumb = document.querySelector("#wayfinding-breadcrumbs_feature_div");
    const category = breadcrumb ? breadcrumb.innerText.split("\n")[0].trim().toLowerCase() : "general";

    return {
      store: "amazon",
      title: title,
      price: price,
      asin: asin,
      category: category,
      url: window.location.href,
      country: host.includes(".co.uk") ? "uk" : host.includes(".de") ? "de" :
              host.includes(".fr") ? "fr" : host.includes(".es") ? "es" :
              host.includes(".it") ? "it" : host.includes(".co.jp") ? "jp" :
              host.includes(".ca") ? "ca" : "us",
    };
  }

  function detectEbayProduct() {
    const titleEl =
      document.querySelector("#itemTitle") ||
      document.querySelector(".x-item-title__mainTitle") ||
      document.querySelector("h1");
    if (!titleEl) return null;

    const title = titleEl.innerText.trim();
    const priceEl =
      document.querySelector("#prcIsum") ||
      document.querySelector(".x-price-primary span") ||
      document.querySelector('[itemprop="price"]');
    const price = priceEl
      ? parseFloat(priceEl.innerText.replace(/[^0-9.]/g, ""))
      : 0;

    // Extract item ID
    const itemMatch = window.location.pathname.match(/itm\/(?:.*\/)?(\d+)/);
    const itemId = itemMatch ? itemMatch[1] : null;

    return {
      store: "ebay",
      title: title,
      price: price,
      asin: itemId,
      category: "general",
      url: window.location.href,
      country: window.location.hostname.includes(".co.uk") ? "uk" :
              window.location.hostname.includes(".de") ? "de" :
              window.location.hostname.includes(".fr") ? "fr" :
              window.location.hostname.includes(".es") ? "es" :
              window.location.hostname.includes(".it") ? "it" : "us",
    };
  }

  // Fetch data from AgentMagnet
  async function fetchAgentMagnetData(product) {
    if (!product || !product.title) return null;
    try {
      const resp = await fetch(
        `${AGENTMAGNET_API}/search?query=${encodeURIComponent(product.title)}&max_results=5&source=${product.store}`
      );
      if (!resp.ok) return null;
      const data = await resp.json();
      
      // Also fetch reviews & price rating
      const [reviewsResp, ratingResp] = await Promise.all([
        fetch(`${AGENTMAGNET_API}/reviews?product_title=${encodeURIComponent(product.title)}`).catch(() => null),
        fetch(`${AGENTMAGNET_API}/price-rating?price=${product.price}&product_title=${encodeURIComponent(product.title)}&category=${product.category}`).catch(() => null),
      ]);

      return {
        results: data.results || [],
        reviews: reviewsResp ? await reviewsResp.json().catch(() => null) : null,
        priceRating: ratingResp ? await ratingResp.json().catch(() => null) : null,
      };
    } catch (e) {
      console.warn("AgentMagnet fetch error:", e);
      return null;
    }
  }

  // Inject overlay
  function injectOverlay(product, data) {
    const root = document.createElement("div");
    root.id = "agentmagnet-root";

    const results = data?.results || [];
    const reviews = data?.reviews || null;
    const rating = data?.priceRating || null;

    // Find best alternative price
    let bestAlt = null;
    for (const r of results) {
      const storeName = (r.store || "").toLowerCase();
      if (storeName !== product.store && r.price > 0) {
        if (!bestAlt || r.price < bestAlt.price) {
          bestAlt = r;
        }
      }
    }

    const avgRating = reviews?.avg_rating || 0;
    const totalReviews = reviews?.total_reviews || 0;

    root.innerHTML = `
      <style>
        #agentmagnet-panel {
          position: fixed;
          top: 80px;
          right: 10px;
          width: 320px;
          background: white;
          border: 2px solid #6c5ce7;
          border-radius: 16px;
          padding: 16px;
          z-index: 999999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          box-shadow: 0 8px 32px rgba(108,92,231,0.2);
          font-size: 14px;
          line-height: 1.5;
          color: #1a1a1a;
          max-height: 80vh;
          overflow-y: auto;
        }
        #agentmagnet-panel h3 {
          margin: 0 0 8px 0;
          font-size: 16px;
          color: #6c5ce7;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        #agentmagnet-panel h3 span { font-size: 12px; color: #999; font-weight: normal; }
        #agentmagnet-panel .am-section {
          margin: 10px 0;
          padding: 10px;
          background: #f8f7ff;
          border-radius: 10px;
        }
        #agentmagnet-panel .am-label {
          font-size: 11px;
          text-transform: uppercase;
          color: #888;
          letter-spacing: 0.5px;
          margin-bottom: 4px;
        }
        #agentmagnet-panel .am-price {
          font-size: 18px;
          font-weight: bold;
          color: #2d3436;
        }
        #agentmagnet-panel .am-savings {
          color: #00b894;
          font-weight: bold;
        }
        #agentmagnet-panel .am-stars {
          color: #fdcb6e;
          font-size: 16px;
        }
        #agentmagnet-panel .am-verdict {
          display: inline-block;
          padding: 3px 10px;
          border-radius: 20px;
          font-weight: bold;
          font-size: 12px;
        }
        #agentmagnet-panel .am-verdict.buy-now { background: #00b894; color: white; }
        #agentmagnet-panel .am-verdict.good { background: #6c5ce7; color: white; }
        #agentmagnet-panel .am-verdict.average { background: #fdcb6e; color: #2d3436; }
        #agentmagnet-panel .am-verdict.bad { background: #e17055; color: white; }
        #agentmagnet-panel .am-btn {
          display: block;
          width: 100%;
          padding: 10px;
          background: #6c5ce7;
          color: white;
          border: none;
          border-radius: 10px;
          font-weight: bold;
          cursor: pointer;
          text-align: center;
          text-decoration: none;
          margin-top: 8px;
          font-size: 13px;
        }
        #agentmagnet-panel .am-btn:hover { background: #5a4bd1; }
        #agentmagnet-panel .am-btn.secondary { background: #dfe6e9; color: #2d3436; }
        #agentmagnet-panel .am-btn.secondary:hover { background: #b2bec3; }
        #agentmagnet-panel .am-close {
          float: right;
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: #999;
          padding: 0;
          line-height: 1;
        }
        #agentmagnet-panel .am-close:hover { color: #e17055; }
        #agentmagnet-panel .am-coupon {
          background: #ffeaa7;
          padding: 4px 8px;
          border-radius: 6px;
          font-size: 12px;
          display: inline-block;
          margin: 2px;
        }
        #agentmagnet-panel .am-footer {
          font-size: 10px;
          color: #b2bec3;
          text-align: center;
          margin-top: 10px;
          border-top: 1px solid #eee;
          padding-top: 8px;
        }
      </style>
      <div id="agentmagnet-panel">
        <button class="am-close" id="am-close">&times;</button>
        <h3>⚡ AgentMagnet <span>AI shopping</span></h3>

        ${bestAlt ? `
          <div class="am-section">
            <div class="am-label">💰 Mejor precio en</div>
            <div class="am-price">${bestAlt.currency || "$"}${bestAlt.price}</div>
            <div style="color:#636e72;font-size:13px;">${bestAlt.store}</div>
            ${product.price > bestAlt.price ? `<div class="am-savings">🔥 Ahorras $${(product.price - bestAlt.price).toFixed(2)}</div>` : ""}
            <a href="${bestAlt.affiliate_url || bestAlt.url || "#"}" class="am-btn" target="_blank">Ver oferta →</a>
          </div>
        ` : `
          <div class="am-section">
            <div class="am-label">💎 Precio actual</div>
            <div class="am-price">${product.currency || "$"}${product.price || "?"}</div>
          </div>
        `}

        ${avgRating > 0 ? `
          <div class="am-section">
            <div class="am-label">⭐ Reviews de AI Agents</div>
            <div class="am-stars">${"★".repeat(Math.round(avgRating))}${"☆".repeat(5 - Math.round(avgRating))}</div>
            <div>${avgRating}/5 de ${totalReviews} agents</div>
          </div>
        ` : ""}

        ${rating ? `
          <div class="am-section">
            <div class="am-label">📊 Price Rating</div>
            <div><span class="am-verdict ${rating.verdict === 'BUY NOW' ? 'buy-now' : rating.verdict === 'Good Deal' ? 'good' : rating.verdict === 'Average' ? 'average' : 'bad'}">${rating.verdict}</span></div>
            <div style="font-size:12px;color:#636e72;margin-top:4px;">${rating.reason}</div>
          </div>
        ` : ""}

        ${results.length > 0 ? `
          <div class="am-section">
            <div class="am-label">🛍️ Disponible en ${results.length} tiendas</div>
            ${results.slice(0, 5).map(r => `
              <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #eee;font-size:13px;">
                <span>${r.store || "?"}</span>
                <span style="font-weight:bold;">${r.currency || "$"}${r.price || "?"}</span>
              </div>
            `).join("")}
          </div>
        ` : ""}

        <div style="display:flex;gap:8px;">
          <a href="https://agentmagnet-y07b.onrender.com/dashboard" class="am-btn secondary" target="_blank" style="flex:1;">📊 Dashboard</a>
          <button class="am-btn secondary" id="am-search-more" style="flex:1;">🔍 Buscar más</button>
        </div>

        <div class="am-footer">
          Powered by AgentMagnet • <a href="https://agentmagnet-y07b.onrender.com" target="_blank" style="color:#6c5ce7;">agentmagnet.io</a>
        </div>
      </div>
    `;

    document.body.appendChild(root);

    // Close button
    document.getElementById("am-close").onclick = () => root.remove();

    // Search more button
    document.getElementById("am-search-more").onclick = () => {
      window.open(`https://agentmagnet-y07b.onrender.com/api/search?query=${encodeURIComponent(product.title)}`, "_blank");
    };
  }

  // Main
  const product = detectProduct();
  if (!product) return;

  fetchAgentMagnetData(product).then((data) => {
    // Wait for page to load fully
    setTimeout(() => injectOverlay(product, data), 1000);
  });
})();
