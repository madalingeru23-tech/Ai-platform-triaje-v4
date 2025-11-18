let currentTriage = null;

function loadTriageFromStorage() {
  const saved = localStorage.getItem("last_triage");
  if (!saved) {
    document.getElementById("noTriage").style.display = "block";
    return;
  }
  try {
    const t = JSON.parse(saved);
    currentTriage = t;

    document.getElementById("noTriage").style.display = "none";
    document.getElementById("triageSummary").style.display = "block";

    const name = [t.first_name || "", t.last_name || ""].join(" ").trim();
    document.getElementById("pacientName").value = name || "—";
    document.getElementById("pacientCnp").value = t.cnp || "";

    const level = t.level || t.triage_level || 3;
    document.getElementById("triageLevelTag").textContent = "Nivel " + level;

    if (t.reason) {
      document.getElementById("reasonInput").value = t.reason;
    }

    // după ce avem triage, cerem sugestia AI
    fetchAiSuggestion();
  } catch (e) {
    console.error("Eroare parsare last_triage:", e);
    document.getElementById("noTriage").style.display = "block";
  }
}

async function fetchAiSuggestion() {
  if (!currentTriage) return;

  const status = document.getElementById("statusMsg");
  status.textContent = "";
  status.className = "";

  const level = currentTriage.level || currentTriage.triage_level || 3;
  const reason = document.getElementById("reasonInput").value || currentTriage.reason || "";

  const payload = {
    triage_level: level,
    reason: reason
  };

  try {
    const res = await fetch("/api/discharge/suggest", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      status.textContent = "Nu s-a putut obține sugestia AI.";
      status.className = "err";
      return;
    }

    const data = await res.json();
    document.getElementById("aiSection").style.display = "block";
    document.getElementById("diagText").value = data.diagnosis || "";
    document.getElementById("evolText").value = data.evolution || "";
    document.getElementById("recText").value = data.recommendations || "";
  } catch (err) {
    console.error("Eroare fetchAiSuggestion:", err);
    status.textContent = "Eroare de rețea la sugestia AI.";
    status.className = "err";
  }
}

async function saveFinalTexts() {
  if (!currentTriage) return;
  const status = document.getElementById("statusMsg");
  status.textContent = "";
  status.className = "";

  const level = currentTriage.level || currentTriage.triage_level || 3;
  const reason = document.getElementById("reasonInput").value || currentTriage.reason || "";

  const payload = {
    triage_level: level,
    reason: reason,
    diagnosis_final: document.getElementById("diagText").value || "",
    evolution_final: document.getElementById("evolText").value || "",
    recommendations_final: document.getElementById("recText").value || ""
  };

  try {
    const res = await fetch("/api/discharge/confirm", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      status.textContent = "Eroare la salvarea datelor finale.";
      status.className = "err";
      return;
    }

    status.textContent = "✅ Textele au fost salvate. AI-ul va folosi această variantă pentru cazuri similare.";
    status.className = "ok";
  } catch (err) {
    console.error("Eroare saveFinalTexts:", err);
    status.textContent = "Eroare de rețea la salvare.";
    status.className = "err";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadTriageFromStorage();

  const refreshBtn = document.getElementById("refreshAiBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", (e) => {
      e.preventDefault();
      fetchAiSuggestion();
    });
  }

  const saveBtn = document.getElementById("saveAiBtn");
  if (saveBtn) {
    saveBtn.addEventListener("click", (e) => {
      e.preventDefault();
      saveFinalTexts();
    });
  }
});
