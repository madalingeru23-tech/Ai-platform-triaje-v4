document.getElementById("analyze").addEventListener("click", () => {
  const hr   = parseInt(document.getElementById("hr").value || "0", 10);
  const spo2 = parseInt(document.getElementById("spo2").value || "0", 10);
  const temp = parseFloat(document.getElementById("temp").value || "0");

  let level = "Verde (fără urgență)";
  let color = "green";

  if (spo2 < 90 || hr > 130 || temp >= 40) { level = "Roșu (urgență majoră)"; color = "red"; }
  else if (spo2 < 94 || hr > 110 || temp >= 38.5) { level = "Galben (urgență medie)"; color = "orange"; }
  else if (hr < 50 || temp < 35) { level = "Portocaliu (intermediar)"; color = "darkorange"; }

  const out = document.getElementById("triageOutput");
  out.textContent = `Nivel de triaj: ${level}`;
  out.style.fontWeight = "700";
  out.style.color = color;

  document.getElementById("result").classList.remove("hidden");
});
