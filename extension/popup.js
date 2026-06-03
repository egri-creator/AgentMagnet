// AgentMagnet popup
const API = "https://agentmagnet-y07b.onrender.com/api";

async function loadStats() {
  try {
    const resp = await fetch(`${API}/stats`);
    const data = await resp.json();
    document.getElementById("agent-count").textContent = data.unique_agents_today || "N/A";
    document.getElementById("search-count").textContent = data.searches_today || "N/A";
  } catch {
    document.getElementById("agent-count").textContent = "offline";
    document.getElementById("search-count").textContent = "offline";
  }
}

document.getElementById("search-btn").onclick = async () => {
  const query = document.getElementById("search-input").value.trim();
  if (!query) return;

  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "<div style='text-align:center;padding:20px;color:#888;'>🔍 Buscando...</div>";

  try {
    const resp = await fetch(`${API}/search?query=${encodeURIComponent(query)}&max_results=5`);
    if (!resp.ok) throw new Error("API error");
    const data = await resp.json();
    const results = data.results || [];

    if (results.length === 0) {
      resultsDiv.innerHTML = "<div style='text-align:center;padding:20px;color:#888;'>No se encontraron resultados</div>";
      return;
    }

    resultsDiv.innerHTML = results.map(r => `
      <div class="result-item">
        <div style="font-weight:500;">${r.title || "?"}</div>
        <div>
          <span class="price">${r.currency || "$"}${r.price || "?"}</span>
          <span class="store">en ${r.store || "?"}</span>
          ${r.rating ? `<span style="color:#fdcb6e;"> ★${r.rating}</span>` : ""}
        </div>
        ${r.affiliate_url ? `<a href="${r.affiliate_url}" target="_blank" style="color:#6c5ce7;font-size:12px;">Ver oferta →</a>` : ""}
      </div>
    `).join("") + 
    `<div style="text-align:center;margin-top:8px;font-size:11px;color:#888;">
      Mostrando ${results.length} de ${data.total_found || results.length} resultados
    </div>`;

  } catch (e) {
    resultsDiv.innerHTML = `<div style='text-align:center;padding:20px;color:#e17055;'>Error: ${e.message}</div>`;
  }
};

// Enter key triggers search
document.getElementById("search-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") document.getElementById("search-btn").click();
});

loadStats();
