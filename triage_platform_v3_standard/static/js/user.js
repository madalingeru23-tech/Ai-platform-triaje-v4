// static/js/user.js
async function loadCurrentDoctor() {
  try {
    const res = await fetch("/api/auth/me");
    if (!res.ok) return;
    const doctor = await res.json();

    // adaugă bară persistentă jos în stânga
    const footer = document.createElement("div");
    footer.id = "doctorFooter";
    footer.innerHTML = `
      👨‍⚕️ <strong>${doctor.full_name}</strong> — ${doctor.specialty}
      <button id="logoutBtn">Deconectare</button>
    `;
    document.body.appendChild(footer);

       const style = document.createElement("style");
    style.textContent = `
      #doctorFooter {
        position: fixed;
        bottom: 12px;
        left: 20px;
        background: rgba(255, 255, 255, 0.9);
        padding: 6px 12px;
        border-radius: 10px;
        font-family: "Inter", sans-serif;
        font-size: 0.85rem;
        color: #222;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 6px;
        z-index: 9999;
      }

      #logoutBtn {
        background: #c62828;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 3px 8px;
        cursor: pointer;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1.1;
        transition: background 0.2s ease;
      }

      #logoutBtn:hover {
        background: #8e0000;
      }
    `;

    document.head.appendChild(style);

    // funcția de logout
    document.getElementById("logoutBtn").addEventListener("click", async () => {
      await fetch("/api/auth/logout", { method: "POST" });
      window.location.href = "/static/login.html";
    });
  } catch (err) {
    console.error("Eroare la încărcarea doctorului curent:", err);
  }
}

// rulează automat la încărcare
document.addEventListener("DOMContentLoaded", loadCurrentDoctor);
