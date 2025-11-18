// static/admissions.js

async function loadAdmissions() {
  const res = await fetch("/api/admissions");
  const list = await res.json();
  const tbody = document.querySelector("#admissionTable tbody");
  tbody.innerHTML = "";

  list.forEach(adm => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${adm.id}</td>
      <td>${adm.first_name}</td>
      <td>${adm.last_name}</td>
      <td>${adm.reason || "-"}</td>
      <td>${adm.triage_color.toUpperCase()}</td>
      <td>${adm.timestamp}</td>
    `;
    tbody.appendChild(row);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("admissionForm");
  const loadListBtn = document.getElementById("loadList");

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const payload = {
      first_name: document.getElementById("first_name").value,
      last_name: document.getElementById("last_name").value,
      reason: document.getElementById("reason").value,
      triage_level: Number(document.getElementById("triage_level").value),
      triage_color: document.getElementById("triage_level").selectedOptions[0].text.split(" - ")[1].toLowerCase(),
    };

    const res = await fetch("/api/admissions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("Pacient internat cu succes!");
      await loadAdmissions();
    } else {
      alert("Eroare la internare!");
    }
  });

  loadListBtn.addEventListener("click", loadAdmissions);
});
