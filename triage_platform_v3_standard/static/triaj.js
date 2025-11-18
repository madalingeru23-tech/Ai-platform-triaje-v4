// =============== Helpers =================

function byId(id) { return document.getElementById(id); }

function valNum(id) {
  const v = byId(id).value.trim();
  if (v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function valStr(id) {
  const v = byId(id).value.trim();
  return v === "" ? null : v;
}

// Sparge tensiunea arterială "120/80"
function parseBP() {
  const raw = byId("bp").value.trim();
  if (!raw.includes("/")) return { sbp: null, dbp: null };
  const [s, d] = raw.split("/");
  const sbp = Number(s);
  const dbp = Number(d);
  return {
    sbp: Number.isFinite(sbp) ? sbp : null,
    dbp: Number.isFinite(dbp) ? dbp : null,
  };
}

// =============== Salvare triaj (format unic și stabil) =================

function saveTriageData(data) {
  const triageData = {
    first_name: byId("first_name")?.value || "",
    last_name:  byId("last_name")?.value || "",
    cnp:        byId("cnp")?.value || "",
    level:      data.level || data.triage_level || data.score_level || 3,
    reason:     data.reason || "",
    timestamp:  Date.now()
  };

  localStorage.setItem("last_triage", JSON.stringify(triageData));
}

// =============== Render rezultat =================

function renderResult(data) {
  const box = document.getElementById("triage_result");
  const { level, color, label, time_target, reasons, advice, normalized } = data;

  box.className = "result-box";
  if (color) box.classList.add(`result-${color}`);

  box.innerHTML = `
    <h3>${label}</h3>
    <p class="muted">⏱ Țintă timp: <strong>${time_target}</strong></p>
    <p><strong>Nivel:</strong> ${level}</p>
    <p><strong>Vârstă/Sex:</strong> ${normalized?.age ?? "-"} / ${normalized?.sex ?? "-"}</p>

    <p><strong>Motive:</strong></p>
    <ul>${(reasons || []).map(r => `<li>${r}</li>`).join("") || "<li>—</li>"}</ul>

    <p><strong>Recomandări:</strong></p>
    <ul>${(advice || []).map(a => `<li>${a}</li>`).join("") || "<li>—</li>"}</ul>

    <div class="actions">
      <button id="goToInternare" class="ghost">Continuă la internare</button>
      <button id="goToAmbulator" class="ghost">Continuă la externare ambulator</button>
    </div>
  `;

  // ====== Buton Internare ======
  const btn = document.getElementById("goToInternare");
  if (btn) {
    btn.addEventListener("click", () => {
      saveTriageData(data);
      window.location.href = "/static/admission.html";
    });
  }

  // ====== Buton Externare Ambulator ======
  const amb = document.getElementById("goToAmbulator");
  if (amb) {
    amb.addEventListener("click", () => {
      saveTriageData(data);
      window.location.href = "/static/externare_ambulatoriu.html";
    });
  }
}

// =============== Loading / Error ===============

function renderLoading() {
  byId("triage_result").innerHTML = `<div class="loading">Se evaluează...</div>`;
}

function renderError(msg) {
  byId("triage_result").innerHTML = `<div class="error">${msg}</div>`;
}

// =============== Submit Triaj =================

async function onSubmit(ev) {
  ev.preventDefault();
  renderLoading();

  const { sbp, dbp } = parseBP();

  const payload = {
    first_name: valStr("first_name"),
    last_name:  valStr("last_name"),
    cnp:        valStr("cnp"),
    age:        valNum("age"),
    sex:        valStr("sex"),
    sbp, dbp,
    hr:   valNum("hr"),
    rr:   valNum("rr"),
    spo2: valNum("spo2"),
    temp: valNum("temp"),
    gcs:  valNum("gcs"),
    pain: valNum("pain"),

    // îl scoatem complet, vezi pasul 2
    // resources_expected: Number(byId("resources_expected").value),

    red_flags: {},
  };

  try {
    const res = await fetch("/api/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json(); // ← SINGURUL JSON

    if (!res.ok) {
      renderError(data.detail || "Eroare la evaluare.");
      return;
    }

    // Normalizăm input
    if (data.normalized) {
      if (data.normalized.age) byId("age").value = data.normalized.age;
      if (data.normalized.sex) byId("sex").value = data.normalized.sex;
    }

    // Salvăm datele de triaj
    saveTriageData(data);

    // Afișăm rezultat
    renderResult(data);

  } catch (err) {
    console.error(err);
    renderError("Eroare: nu s-a putut face evaluarea.");
  }
}


// =============== Reset =================

function onReset() {
  byId("triageForm").reset();
  byId("triage_result").innerHTML =
    `<em>Completează datele și apasă „Evaluează pacientul”.</em>`;
}

// =============== Autofill CNP =================

window.addEventListener("DOMContentLoaded", () => {
  const form = byId("triageForm");

  const cnpInput = byId("cnp");
  cnpInput.addEventListener("input", () => {
    const cnp = cnpInput.value.trim();
    if (cnp.length === 13 && /^\d{13}$/.test(cnp)) {
      const s = parseInt(cnp[0]);
      const yy = parseInt(cnp.substring(1, 3));
      const mm = parseInt(cnp.substring(3, 5));
      const dd = parseInt(cnp.substring(5, 7));

      let year = s < 3 ? 1900 + yy : s < 5 ? 1800 + yy : 2000 + yy;
      const sex = (s % 2 === 1) ? "M" : "F";

      const today = new Date();
      const birth = new Date(year, mm - 1, dd);
      let age = today.getFullYear() - birth.getFullYear();
      const m = today.getMonth() - birth.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;

      if (age >= 0 && age < 120) byId("age").value = age;
      byId("sex").value = sex;
    }
  });

  form.addEventListener("submit", onSubmit);
  byId("resetBtn").addEventListener("click", onReset);
});
