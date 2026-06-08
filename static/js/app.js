/**
 * IP Manager — app.js
 * Secciones: IPv4 · IPv6 · Historial
 */

"use strict";

// ══════════════════════════════════════════════════════════
//  UTILIDADES
// ══════════════════════════════════════════════════════════

function showToast(message, type = "success") {
  const toast = document.getElementById("toast-notif");
  const msg   = document.getElementById("toast-msg");
  toast.classList.remove("bg-success","bg-danger","bg-warning","bg-secondary","bg-info");
  toast.classList.add(`bg-${type}`);
  msg.textContent = message;
  bootstrap.Toast.getOrCreateInstance(toast, { delay: 3500 }).show();
}

function boolBadge(val) {
  return val
    ? `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Sí</span>`
    : `<span class="badge bg-secondary"><i class="bi bi-x-circle me-1"></i>No</span>`;
}

function classificationColor(cls) {
  const map = {
    "Pública":        "card-gradient-blue",
    "Privada":        "card-gradient-green",
    "Loopback":       "card-gradient-purple",
    "Multicast":      "card-gradient-orange",
    "Reservada":      "card-gradient-red",
    "Especial":       "card-gradient-indigo",
    "Link-Local":     "card-gradient-teal",
    "Privada (ULA)":  "card-gradient-teal",
    "Global Unicast": "card-gradient-blue",
  };
  return map[cls] || "card-gradient-cyan";
}

async function exportJSON(data, filename) {
  try {
    const resp = await fetch("/api/export/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data, filename }),
    });
    if (!resp.ok) throw new Error("Error al exportar");
    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement("a"), {
      href: url, download: `${filename || "resultado"}.json`
    });
    a.click();
    URL.revokeObjectURL(url);
    showToast("Archivo exportado.", "success");
  } catch (err) {
    showToast("Error al exportar: " + err.message, "danger");
  }
}

// Sincronizar sliders
function syncSlider(inputId, sliderId) {
  const inp = document.getElementById(inputId);
  const sld = document.getElementById(sliderId);
  if (!inp || !sld) return;
  sld.addEventListener("input", () => { inp.value = sld.value; });
  inp.addEventListener("input", () => { const v = parseInt(inp.value); if (!isNaN(v)) sld.value = v; });
}
syncSlider("ipv4-cidr",   "ipv4-cidr-slider");
syncSlider("ipv6-prefix", "ipv6-prefix-slider");


// ══════════════════════════════════════════════════════════
//  SECCIÓN IPv4
// ══════════════════════════════════════════════════════════

let lastIPv4Result = null;

function buildIPv4SummaryCards(d) {
  const cc = classificationColor(d.classification);
  return [
    { label:"Red",            value:d.network_address,               icon:"bi-diagram-3",   g:"card-gradient-blue"   },
    { label:"Broadcast",      value:d.broadcast_address,             icon:"bi-broadcast",   g:"card-gradient-orange" },
    { label:"Máscara / CIDR", value:`${d.mask} / ${d.cidr}`,         icon:"bi-filter",      g:"card-gradient-purple" },
    { label:"Hosts útiles",   value:d.usable_hosts.toLocaleString(),  icon:"bi-people",      g:"card-gradient-green"  },
    { label:"Primer Host",    value:d.first_host,                    icon:"bi-caret-right",  g:"card-gradient-teal"   },
    { label:"Último Host",    value:d.last_host,                     icon:"bi-caret-left",   g:"card-gradient-cyan"   },
    { label:"Clasificación",  value:d.classification,                icon:"bi-tag",          g:cc                     },
    { label:"Clase IP",       value:d.ip_class,                      icon:"bi-alphabet",     g:"card-gradient-indigo" },
  ].map(c => `
    <div class="col-6 col-sm-6 col-md-3">
      <div class="summary-card ${c.g} d-flex justify-content-between align-items-center">
        <div><div class="label">${c.label}</div><div class="value">${c.value}</div></div>
        <i class="bi ${c.icon} icon"></i>
      </div>
    </div>`).join("");
}

function buildIPv4Table(d) {
  return [
    ["Dirección IP",         `<code>${d.ip}</code>`],
    ["Red",                  `<code>${d.network_address}</code>`],
    ["Broadcast",            `<code>${d.broadcast_address}</code>`],
    ["Máscara de subred",    `<code>${d.mask}</code>`],
    ["Prefijo CIDR",         `<code>/${d.cidr}</code>`],
    ["Wildcard / Inversa",   `<code>${d.wildcard}</code>`],
    ["Primer host usable",   `<code>${d.first_host}</code>`],
    ["Último host usable",   `<code>${d.last_host}</code>`],
    ["Total de direcciones", `<code>${d.total_hosts.toLocaleString()}</code>`],
    ["Hosts utilizables",    `<code>${d.usable_hosts.toLocaleString()}</code>`],
    ["Clase IP",             `<code>${d.ip_class}</code>`],
    ["Clasificación",        `<span class="badge bg-primary">${d.classification}</span>`],
    ["¿Es privada?",         boolBadge(d.is_private)],
    ["¿Es loopback?",        boolBadge(d.is_loopback)],
    ["¿Es multicast?",       boolBadge(d.is_multicast)],
    ["¿Es reservada?",       boolBadge(d.is_reserved)],
    ["Máscara en binario",   `<code class="small">${d.binary_mask}</code>`],
    ["Red en binario",       `<code class="small">${d.network_binary}</code>`],
  ].map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join("");
}

document.getElementById("form-ipv4").addEventListener("submit", async (e) => {
  e.preventDefault();
  const ip   = document.getElementById("ipv4-ip").value.trim();
  const mask = document.getElementById("ipv4-mask").value.trim() || null;
  const cidr = document.getElementById("ipv4-cidr").value.trim();
  if (!ip) { showToast("Ingresa una dirección IPv4.", "warning"); return; }

  const payload = { ip };
  if (mask) payload.mask = mask;
  if (cidr !== "") payload.cidr = parseInt(cidr);

  const ph = document.getElementById("ipv4-placeholder");
  ph.innerHTML = `<div class="loading-overlay"><div class="spinner-border text-primary"></div><span>Calculando…</span></div>`;

  try {
    const resp = await fetch("/api/ipv4/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      showToast(data.detail || "Error al calcular.", "danger");
      ph.innerHTML = `<div class="text-center text-danger py-5"><i class="bi bi-exclamation-triangle display-1 d-block mb-3"></i><p>${data.detail}</p></div>`;
      return;
    }
    lastIPv4Result = data;
    document.getElementById("ipv4-summary-cards").innerHTML = buildIPv4SummaryCards(data);
    document.getElementById("ipv4-tbody").innerHTML         = buildIPv4Table(data);
    ph.classList.add("d-none");
    document.getElementById("ipv4-results").classList.remove("d-none");
    showToast(`IPv4: ${data.network_address}/${data.cidr}`, "success");
  } catch (err) {
    showToast("Error de conexión: " + err.message, "danger");
  }
});

document.getElementById("btn-ipv4-clear").addEventListener("click", () => {
  ["ipv4-ip","ipv4-mask","ipv4-cidr"].forEach(id => document.getElementById(id).value = "");
  document.getElementById("ipv4-cidr-slider").value = 0;
  document.getElementById("ipv4-results").classList.add("d-none");
  const ph = document.getElementById("ipv4-placeholder");
  ph.innerHTML = `<div class="text-center text-muted py-5">
    <i class="bi bi-calculator display-1 mb-3 d-block"></i>
    <p class="fs-5">Completa el formulario y presiona <strong>Calcular IPv4</strong></p>
  </div>`;
  ph.classList.remove("d-none");
  lastIPv4Result = null;
});

document.getElementById("btn-export-ipv4").addEventListener("click", () => {
  if (lastIPv4Result) exportJSON(lastIPv4Result, `ipv4_${lastIPv4Result.ip}_${lastIPv4Result.cidr}`);
  else showToast("Primero calcula una dirección IPv4.", "warning");
});


// ══════════════════════════════════════════════════════════
//  SECCIÓN IPv6
// ══════════════════════════════════════════════════════════

let lastIPv6Result = null;

function buildIPv6SummaryCards(d) {
  const cc = classificationColor(d.ip_type);
  return [
    { label:"Comprimida",    value:d.compressed,   icon:"bi-compress",  g:"card-gradient-blue"   },
    { label:"Red / Prefijo", value:`/${d.prefix}`, icon:"bi-diagram-3", g:"card-gradient-purple" },
    { label:"Tipo",          value:d.ip_type,       icon:"bi-tag",       g:cc                     },
    { label:"Alcance",       value:d.scope,         icon:"bi-globe2",    g:"card-gradient-teal"   },
  ].map(c => `
    <div class="col-6 col-sm-6 col-md-3">
      <div class="summary-card ${c.g} d-flex justify-content-between align-items-center">
        <div><div class="label">${c.label}</div><div class="value">${c.value}</div></div>
        <i class="bi ${c.icon} icon"></i>
      </div>
    </div>`).join("");
}

function buildIPv6Table(d) {
  return [
    ["Dirección original",   `<code>${d.ip}</code>`],
    ["Forma expandida",      `<code class="small">${d.expanded}</code>`],
    ["Forma comprimida",     `<code>${d.compressed}</code>`],
    ["Prefijo",              `<code>/${d.prefix}</code>`],
    ["Dirección de red",     `<code>${d.network_address}</code>`],
    ["Total de direcciones", `<code>${d.total_addresses}</code>`],
    ["Tipo",                 `<code>${d.ip_type}</code>`],
    ["Alcance",              `<code>${d.scope}</code>`],
    ["¿Es loopback?",        boolBadge(d.is_loopback)],
    ["¿Es multicast?",       boolBadge(d.is_multicast)],
    ["¿Es link-local?",      boolBadge(d.is_link_local)],
    ["¿Es privada (ULA)?",   boolBadge(d.is_private)],
  ].map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join("");
}

document.getElementById("form-ipv6").addEventListener("submit", async (e) => {
  e.preventDefault();
  const ip     = document.getElementById("ipv6-ip").value.trim();
  const prefix = document.getElementById("ipv6-prefix").value.trim();
  if (!ip) { showToast("Ingresa una dirección IPv6.", "warning"); return; }

  const payload = { ip };
  if (prefix !== "") payload.prefix = parseInt(prefix);

  const ph = document.getElementById("ipv6-placeholder");
  ph.innerHTML = `<div class="loading-overlay"><div class="spinner-border text-info"></div><span>Calculando…</span></div>`;

  try {
    const resp = await fetch("/api/ipv6/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) {
      showToast(data.detail || "Error al calcular.", "danger");
      ph.innerHTML = `<div class="text-center text-danger py-5"><i class="bi bi-exclamation-triangle display-1 d-block mb-3"></i><p>${data.detail}</p></div>`;
      return;
    }
    lastIPv6Result = data;
    document.getElementById("ipv6-summary-cards").innerHTML = buildIPv6SummaryCards(data);
    document.getElementById("ipv6-tbody").innerHTML         = buildIPv6Table(data);
    ph.classList.add("d-none");
    document.getElementById("ipv6-results").classList.remove("d-none");
    showToast(`IPv6: ${data.compressed}/${data.prefix}`, "success");
  } catch (err) {
    showToast("Error de conexión: " + err.message, "danger");
  }
});

document.getElementById("btn-ipv6-clear").addEventListener("click", () => {
  ["ipv6-ip","ipv6-prefix"].forEach(id => document.getElementById(id).value = "");
  document.getElementById("ipv6-prefix-slider").value = 0;
  document.getElementById("ipv6-results").classList.add("d-none");
  const ph = document.getElementById("ipv6-placeholder");
  ph.innerHTML = `<div class="text-center text-muted py-5">
    <i class="bi bi-globe display-1 mb-3 d-block"></i>
    <p class="fs-5">Completa el formulario y presiona <strong>Calcular IPv6</strong></p>
  </div>`;
  ph.classList.remove("d-none");
  lastIPv6Result = null;
});

document.getElementById("btn-export-ipv6").addEventListener("click", () => {
  if (lastIPv6Result) exportJSON(lastIPv6Result, `ipv6_${lastIPv6Result.compressed.replace(/:/g,"-")}_${lastIPv6Result.prefix}`);
  else showToast("Primero calcula una dirección IPv6.", "warning");
});


// ══════════════════════════════════════════════════════════
//  RED LOCAL (INTERFACES WINDOWS)
// ══════════════════════════════════════════════════════════

async function loadLocalInterfaces() {
  const grid   = document.getElementById("local-interfaces-grid");
  const ph     = document.getElementById("local-interfaces-placeholder");
  const badge  = document.getElementById("local-agent-badge");

  ph.innerHTML = `<div class="loading-overlay"><div class="spinner-border text-warning"></div><span>Consultando agente local…</span></div>`;
  ph.classList.remove("d-none");
  grid.classList.add("d-none");

  try {
    const resp = await fetch("/api/local/interfaces");
    const data = await resp.json();

    if (!resp.ok) {
      badge.className = "badge bg-danger";
      badge.textContent = "Agente desconectado";
      ph.innerHTML = `<div class="text-center text-danger py-4">
        <i class="bi bi-exclamation-triangle display-4 d-block mb-3"></i>
        <p>${data.detail || "No se pudo conectar al agente local."}</p>
        <p class="small text-muted">Ejecuta: <code>python local_agent.py</code></p>
      </div>`;
      return;
    }

    badge.className = "badge bg-success";
    badge.textContent = `Agente activo · ${data.total} interfaz${data.total !== 1 ? "es" : ""}`;

    if (!data.interfaces || data.interfaces.length === 0) {
      ph.innerHTML = `<p class="text-center text-muted py-3">No se encontraron interfaces.</p>`;
      return;
    }

    grid.innerHTML = data.interfaces.map(iface => {
      const upClass  = iface.is_up ? "border-success" : "border-secondary";
      const upBadge  = iface.is_up
        ? `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Activa</span>`
        : `<span class="badge bg-secondary"><i class="bi bi-x-circle me-1"></i>Inactiva</span>`;
      const speedTxt = iface.speed_mbps > 0 ? `${iface.speed_mbps} Mbps` : "—";

      const ipv4Html = iface.ipv4
        ? `<span class="badge bg-primary font-mono iface-ip" style="cursor:pointer" title="Calcular IPv4" data-ip="${iface.ipv4}" data-type="v4">${iface.ipv4}${iface.cidr ? "/" + iface.cidr : ""}</span>`
        : `<span class="text-muted small">—</span>`;
      const ipv6Html = iface.ipv6
        ? `<span class="badge bg-info font-mono iface-ip" style="cursor:pointer" title="Calcular IPv6" data-ip="${iface.ipv6}" data-type="v6">${iface.ipv6}</span>`
        : `<span class="text-muted small">—</span>`;

      return `
        <div class="col-12 col-md-6 col-xl-4">
          <div class="card h-100 border ${upClass}">
            <div class="card-header d-flex justify-content-between align-items-center py-2">
              <strong class="text-truncate me-2">${iface.name}</strong>
              ${upBadge}
            </div>
            <div class="card-body small p-3">
              <div class="mb-1"><i class="bi bi-4-circle text-primary me-1"></i><strong>IPv4:</strong> ${ipv4Html}</div>
              <div class="mb-1"><i class="bi bi-6-circle text-info me-1"></i><strong>IPv6:</strong> ${ipv6Html}</div>
              <div class="mb-1"><i class="bi bi-ethernet me-1"></i><strong>MAC:</strong> <code>${iface.mac || "—"}</code></div>
              <hr class="my-2" />
              <div class="d-flex justify-content-between text-muted">
                <span><i class="bi bi-upload me-1"></i>${iface.total_sent_human}</span>
                <span><i class="bi bi-download me-1"></i>${iface.total_recv_human}</span>
                <span><i class="bi bi-speedometer2 me-1"></i>${speedTxt}</span>
              </div>
            </div>
          </div>
        </div>`;
    }).join("");

    ph.classList.add("d-none");
    grid.classList.remove("d-none");

    // Click en IP → llenar formulario correspondiente y hacer scroll
    grid.querySelectorAll(".iface-ip").forEach(el => {
      el.addEventListener("click", () => {
        const ip   = el.dataset.ip;
        const type = el.dataset.type;
        if (type === "v4") {
          document.getElementById("ipv4-ip").value   = ip;
          document.getElementById("ipv4-mask").value = "";
          document.getElementById("ipv4-cidr").value = el.dataset.ip.includes("/")
            ? el.dataset.ip.split("/")[1] : "24";
          document.getElementById("ipv4-cidr-slider").value =
            document.getElementById("ipv4-cidr").value;
          document.getElementById("section-ipv4").scrollIntoView({ behavior: "smooth" });
          document.getElementById("form-ipv4").dispatchEvent(new Event("submit"));
        } else {
          document.getElementById("ipv6-ip").value = ip;
          document.getElementById("section-ipv6").scrollIntoView({ behavior: "smooth" });
          document.getElementById("form-ipv6").dispatchEvent(new Event("submit"));
        }
        showToast(`Calculando ${type === "v4" ? "IPv4" : "IPv6"}: ${ip}`, "info");
      });
    });

  } catch (err) {
    badge.className = "badge bg-danger";
    badge.textContent = "Agente desconectado";
    ph.innerHTML = `<div class="text-center text-danger py-4">
      <i class="bi bi-exclamation-triangle display-4 d-block mb-2"></i>
      <p>Error de conexión: ${err.message}</p>
      <p class="small text-muted">Ejecuta: <code>python local_agent.py</code></p>
    </div>`;
    ph.classList.remove("d-none");
    grid.classList.add("d-none");
  }
}

document.getElementById("btn-refresh-local").addEventListener("click", loadLocalInterfaces);


// ══════════════════════════════════════════════════════════
//  HISTORIAL
// ══════════════════════════════════════════════════════════

async function loadHistory() {
  const tbody = document.getElementById("history-tbody");
  tbody.innerHTML = `<tr><td colspan="5" class="text-center">
    <div class="spinner-border spinner-border-sm text-secondary me-2"></div>Cargando…
  </td></tr>`;
  try {
    const resp = await fetch("/api/history");
    const data = await resp.json();
    if (!data.entries || data.entries.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">No hay consultas en el historial.</td></tr>`;
      return;
    }
    tbody.innerHTML = [...data.entries].reverse().map(e => `
      <tr>
        <td>${e.id}</td>
        <td>${e.timestamp.replace("T"," ")}</td>
        <td><span class="badge bg-primary">${e.operation}</span></td>
        <td>${e.input}</td>
        <td>${e.result_summary}</td>
      </tr>`).join("");
  } catch {
    tbody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">Error al cargar historial.</td></tr>`;
  }
}

document.getElementById("btn-refresh-history").addEventListener("click", loadHistory);

document.getElementById("btn-clear-history").addEventListener("click", async () => {
  if (!confirm("¿Limpiar todo el historial?")) return;
  await fetch("/api/history", { method: "DELETE" });
  showToast("Historial limpiado.", "success");
  loadHistory();
});


// ══════════════════════════════════════════════════════════
//  INICIALIZACIÓN
// ══════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      const t = document.querySelector(a.getAttribute("href"));
      if (t) { e.preventDefault(); t.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  });
});
