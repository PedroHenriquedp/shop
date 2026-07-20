const RESULTS_API_URL = "/api/resultados";
const LIVE_API_URL = "/api/teste-ao-vivo";
const labels = { insercao: "Inserção", busca_existente: "Busca existente", busca_inexistente: "Busca inexistente", remocao: "Remoção", vendas: "Vendas", operacoes_mistas: "Operações mistas", listagem_codigo: "Listagem ordenada" };
const formatSeconds = (value) => `${Number(value).toFixed(6)} s`;
const formatNumber = (value, digits = 0) => Number(value).toLocaleString("pt-BR", { maximumFractionDigits: digits });
let dados;

function resultado(estrutura, cenario, base) { return dados.resultados.find((item) => item.estrutura === estrutura && item.cenario === cenario && item.tamanho_base === base); }
function stat(label, value) { return `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`; }
function preencherFiltros() {
  const base = document.querySelector("#baseSelect"); const scenario = document.querySelector("#scenarioSelect");
  base.innerHTML = dados.metodologia.bases.map((item) => `<option value="${item}">${formatNumber(item)} produtos</option>`).join("");
  scenario.innerHTML = dados.metodologia.cenarios.map((item) => `<option value="${item}">${labels[item]}</option>`).join("");
  base.value = "10000"; scenario.value = "insercao";
}
function officialRow(base, cenario) {
  const hash = resultado("hash", cenario, base); const avl = resultado("avl", cenario, base);
  const vencedor = hash.tempo_medio_segundos < avl.tempo_medio_segundos ? "Hash" : "AVL";
  return `<tr><td>${labels[cenario]}</td><td class="hash-cell">${formatSeconds(hash.tempo_medio_segundos)} ± ${formatSeconds(hash.tempo_desvio_segundos)}</td><td class="avl-cell">${formatSeconds(avl.tempo_medio_segundos)} ± ${formatSeconds(avl.tempo_desvio_segundos)}</td><td>${vencedor}</td></tr>`;
}
function renderChart(cenario) {
  const svg = document.querySelector("#performanceChart"); const bases = dados.metodologia.bases; const width = 760; const height = 260; const left = 58; const right = 26; const top = 24; const bottom = 42;
  const values = bases.flatMap((base) => [resultado("hash", cenario, base).tempo_medio_segundos, resultado("avl", cenario, base).tempo_medio_segundos]); const max = Math.max(...values) || 1;
  const x = (index) => left + (index * (width - left - right)) / (bases.length - 1); const y = (value) => top + (height - top - bottom) * (1 - value / max);
  const line = (estrutura) => bases.map((base, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(1)},${y(resultado(estrutura, cenario, base).tempo_medio_segundos).toFixed(1)}`).join(" ");
  const markers = (estrutura, cssClass) => bases.map((base, index) => `<circle class="${cssClass}" cx="${x(index)}" cy="${y(resultado(estrutura, cenario, base).tempo_medio_segundos)}" r="4" />`).join("");
  const grid = [0, .5, 1].map((fraction) => { const value = max * fraction; const position = y(value); return `<line class="chart-grid" x1="${left}" y1="${position}" x2="${width - right}" y2="${position}" /><text class="chart-label" x="${left - 8}" y="${position + 3}" text-anchor="end">${formatSeconds(value)}</text>`; }).join("");
  const labelsX = bases.map((base, index) => `<text class="chart-label" x="${x(index)}" y="${height - 14}" text-anchor="middle">${formatNumber(base)}</text>`).join("");
  svg.innerHTML = `${grid}<text class="chart-title" x="${width / 2}" y="16" text-anchor="middle">Tempo médio por tamanho de base</text><line class="chart-axis" x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" /><path class="chart-hash" d="${line("hash")}" /><path class="chart-avl" d="${line("avl")}" />${markers("hash", "chart-hash")} ${markers("avl", "chart-avl")} ${labelsX}<text class="chart-axis-title" x="${width / 2}" y="${height - 2}" text-anchor="middle">Quantidade de produtos</text><text class="chart-legend" x="${width - 110}" y="16" fill="#2563eb">Hash</text><text class="chart-legend" x="${width - 58}" y="16" fill="#0f9f6e">AVL</text>`;
}
function renderLiveChart(resultados) {
  const svg = document.querySelector("#livePerformanceChart"); const cenarios = dados.metodologia.cenarios; const width = 760; const height = 300; const left = 58; const right = 26; const top = 28; const bottom = 72;
  const porCenario = (estrutura, cenario) => resultados.find((item) => item.estrutura === estrutura && item.cenario === cenario);
  const values = cenarios.flatMap((cenario) => [porCenario("hash", cenario).tempo_total_segundos, porCenario("avl", cenario).tempo_total_segundos]); const max = Math.max(...values) || 1;
  const x = (index) => left + (index * (width - left - right)) / (cenarios.length - 1); const y = (value) => top + (height - top - bottom) * (1 - value / max);
  const line = (estrutura) => cenarios.map((cenario, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(1)},${y(porCenario(estrutura, cenario).tempo_total_segundos).toFixed(1)}`).join(" ");
  const markers = (estrutura, cssClass) => cenarios.map((cenario, index) => `<circle class="${cssClass}" cx="${x(index)}" cy="${y(porCenario(estrutura, cenario).tempo_total_segundos)}" r="4" />`).join("");
  const grid = [0, .5, 1].map((fraction) => { const value = max * fraction; const position = y(value); return `<line class="chart-grid" x1="${left}" y1="${position}" x2="${width - right}" y2="${position}" /><text class="chart-label" x="${left - 8}" y="${position + 3}" text-anchor="end">${formatSeconds(value)}</text>`; }).join("");
  const shortLabels = { insercao: "Inserção", busca_existente: "Busca exis.", busca_inexistente: "Busca ines.", remocao: "Remoção", vendas: "Vendas", operacoes_mistas: "Mistas", listagem_codigo: "Listagem" };
  const labelsX = cenarios.map((cenario, index) => `<text class="chart-label" x="${x(index)}" y="${height - 45}" text-anchor="middle" transform="rotate(-24 ${x(index)} ${height - 45})">${shortLabels[cenario]}</text>`).join("");
  svg.innerHTML = `${grid}<text class="chart-title" x="${width / 2}" y="16" text-anchor="middle">Tempo da rodada por cenário</text><line class="chart-axis" x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" /><path class="chart-hash" d="${line("hash")}" /><path class="chart-avl" d="${line("avl")}" />${markers("hash", "chart-hash")} ${markers("avl", "chart-avl")} ${labelsX}<text class="chart-axis-title" x="${width / 2}" y="${height - 4}" text-anchor="middle">Cenários da metodologia</text><text class="chart-legend" x="${width - 110}" y="16" fill="#2563eb">Hash</text><text class="chart-legend" x="${width - 58}" y="16" fill="#0f9f6e">AVL</text>`;
}
function renderSelected() {
  const base = Number(document.querySelector("#baseSelect").value); const cenario = document.querySelector("#scenarioSelect").value;
  const hash = resultado("hash", cenario, base); const avl = resultado("avl", cenario, base); const hashWins = hash.tempo_medio_segundos < avl.tempo_medio_segundos; const ratio = avl.tempo_medio_segundos / hash.tempo_medio_segundos; const max = Math.max(hash.tempo_medio_segundos, avl.tempo_medio_segundos);
  document.querySelector("#winner").textContent = hashWins ? "Hash" : "AVL"; document.querySelector("#hashTime").textContent = formatSeconds(hash.tempo_medio_segundos); document.querySelector("#avlTime").textContent = formatSeconds(avl.tempo_medio_segundos); document.querySelector("#speedup").textContent = `${ratio.toFixed(2)}x`;
  document.querySelector("#comparisonDescription").textContent = `${labels[cenario]} com ${formatNumber(base)} produtos e ${hash.quantidade_operacoes} operações por repetição.`;
  document.querySelector("#timeBars").innerHTML = [hash, avl].map((item) => `<div class="bar-row ${item.estrutura}"><span>${item.estrutura.toUpperCase()}</span><div class="bar-track"><div class="bar-fill" style="width:${(item.tempo_medio_segundos / max) * 100}%"></div></div><strong>${formatSeconds(item.tempo_medio_segundos)}</strong><small>± ${formatSeconds(item.tempo_desvio_segundos)}</small></div>`).join("");
  document.querySelector("#hashMetrics").innerHTML = [stat("Operações", formatNumber(hash.quantidade_operacoes)), stat("Memória pico", `${formatNumber(hash.memoria_pico_media_bytes)} B`), stat("Comparações", formatNumber(hash.comparacoes_media)), stat("Colisões", hash.colisoes_media === null ? "-" : formatNumber(hash.colisoes_media)), stat("Fator de carga", hash.fator_carga_medio === null ? "-" : hash.fator_carga_medio.toFixed(3)), stat("Maior lista", hash.maior_lista_media === null ? "-" : formatNumber(hash.maior_lista_media))].join("");
  document.querySelector("#avlMetrics").innerHTML = [stat("Operações", formatNumber(avl.quantidade_operacoes)), stat("Memória pico", `${formatNumber(avl.memoria_pico_media_bytes)} B`), stat("Comparações", formatNumber(avl.comparacoes_media)), stat("Rotações", avl.rotacoes_media === null ? "-" : formatNumber(avl.rotacoes_media)), stat("Altura", avl.altura_media === null ? "-" : formatNumber(avl.altura_media)), stat("Sucessos médios", formatNumber(avl.operacoes_sucesso_media))].join("");
  document.querySelector("#resultsTable").innerHTML = dados.metodologia.cenarios.map((item) => officialRow(base, item)).join("");
  renderChart(cenario);
}
function configurarAbas() {
  document.querySelectorAll(".tab").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item === button));
    document.querySelectorAll("main > section[id]").forEach((view) => view.classList.toggle("hidden", view.id !== button.dataset.view));
  }));
}
async function executarTesteAoVivo(event) {
  event.preventDefault(); const quantidade = Number(document.querySelector("#liveQuantityInput").value); const button = document.querySelector("#liveButton"); const processing = document.querySelector("#liveProcessing"); const status = document.querySelector("#liveStatus");
  if (!Number.isInteger(quantidade) || quantidade < 1 || quantidade > 100000) { status.textContent = "Informe uma quantidade inteira entre 1 e 100.000 produtos."; return; }
  button.disabled = true; processing.classList.remove("hidden"); status.textContent = `Executando uma rodada com ${formatNumber(quantidade)} produtos...`;
  try {
    const response = await fetch(`${LIVE_API_URL}?quantidade=${quantidade}`); const payload = await response.json(); if (!response.ok) throw new Error(payload.erro || "Não foi possível executar o teste.");
    const porCenario = (estrutura, cenario) => payload.resultados.find((item) => item.estrutura === estrutura && item.cenario === cenario);
    document.querySelector("#liveBase").textContent = `${formatNumber(payload.tamanho_base)} produtos`;
    document.querySelector("#liveOrigin").textContent = payload.origem;
    renderLiveChart(payload.resultados);
    document.querySelector("#liveTable").innerHTML = dados.metodologia.cenarios.map((cenario) => { const hash = porCenario("hash", cenario); const avl = porCenario("avl", cenario); const vencedor = hash.tempo_total_segundos < avl.tempo_total_segundos ? "Hash" : "AVL"; return `<tr><td>${labels[cenario]}</td><td class="hash-cell">${formatSeconds(hash.tempo_total_segundos)}</td><td class="avl-cell">${formatSeconds(avl.tempo_total_segundos)}</td><td>${vencedor}</td></tr>`; }).join("");
    document.querySelector("#liveResult").classList.remove("hidden"); status.textContent = "Rodada concluída. Execute novamente para substituir este resultado.";
  } catch (error) { status.textContent = error.message; } finally { processing.classList.add("hidden"); button.disabled = false; }
}
async function iniciar() {
  const response = await fetch(RESULTS_API_URL); if (!response.ok) throw new Error("Não foi possível carregar os resultados experimentais."); dados = await response.json();
  document.querySelector("#methodology").textContent = `${dados.metodologia.repeticoes} repetições · ${dados.metodologia.linhas_brutas} medições`;
  preencherFiltros(); renderSelected(); configurarAbas();
  document.querySelector("#baseSelect").addEventListener("change", renderSelected); document.querySelector("#scenarioSelect").addEventListener("change", renderSelected); document.querySelector("#liveForm").addEventListener("submit", executarTesteAoVivo);
}
iniciar().catch((error) => { document.querySelector("main").innerHTML = `<p class="error">${error.message}</p>`; });
