const api = "http://127.0.0.1:8000/api";

// 🧍 Pacienți
document.getElementById("patientForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    first_name: document.getElementById("first_name").value,
    last_name: document.getElementById("last_name").value,
    age: parseInt(document.getElementById("age").value) || null,
    sex: document.getElementById("sex").value || null,
  };
  await fetch(`${api}/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  loadPatients();
});

async function loadPatients() {
  const res = await fetch(`${api}/patients`);
  const patients = await res.json();
  const list = document.getElementById("patientList");
  list.innerHTML = "";
  patients.forEach((p) => {
    const li = document.createElement("li");
    li.textContent = `${p.first_name} ${p.last_name} (ID: ${p.id})`;
    list.appendChild(li);
  });
}
loadPatients();

// 🏥 Internări
document.getElementById("admissionForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    patient_id: document.getElementById("patient_id").value,
    reason: document.getElementById("reason").value,
    triage_level: document.getElementById("triage_level").value,
  };
  await fetch(`${api}/admissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  loadAdmissions();
});

async function loadAdmissions() {
  const res = await fetch(`${api}/admissions`);
  const admissions = await res.json();
  const list = document.getElementById("admissionList");
  list.innerHTML = "";
  admissions.forEach((a) => {
    const li = document.createElement("li");
    li.textContent = `Internare #${a.id} — Pacient ${a.patient_id}, motiv: ${a.reason || "-"}, triaj: ${a.triage_level || "-"}`;
    list.appendChild(li);
  });
}
loadAdmissions();

// 🗺️ Hartă
document.getElementById("loadWardmap").addEventListener("click", async () => {
  const res = await fetch(`${api}/wardmap`);
  const data = await res.json();
  document.getElementById("wardmapData").textContent = JSON.stringify(data, null, 2);
});
