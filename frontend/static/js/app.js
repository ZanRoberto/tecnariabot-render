// ============================================================================
// TEKNARIA V3 - Frontend App
// ============================================================================

let token = localStorage.getItem("teknaria_token");
let cassetti = [];
let bilanci = [];
let current_cassetto_id = null;

// ============================================================================
// AUTH
// ============================================================================

async function login() {
    const password = document.getElementById("password").value;
    if (!password) {
        alert("Inserisci password");
        return;
    }

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password })
        });

        if (!res.ok) {
            alert("Password scorretta");
            return;
        }

        const data = await res.json();
        token = data.token;
        localStorage.setItem("teknaria_token", token);
        
        showScreen("dashboard");
        loadCassetti();
    } catch (e) {
        alert("Errore login: " + e.message);
    }
}

function logout() {
    token = null;
    localStorage.removeItem("teknaria_token");
    showScreen("login-screen");
}

// ============================================================================
// SCREENS
// ============================================================================

function showScreen(screenId) {
    document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
    document.getElementById(screenId).classList.add("active");
}

// ============================================================================
// CASSETTI
// ============================================================================

async function loadCassetti() {
    try {
        const res = await fetch(`/api/cassetti?token=${token}`);
        const data = await res.json();
        cassetti = data;
        
        const list = document.getElementById("cassetti-list");
        list.innerHTML = "";
        cassetti.forEach(c => {
            const div = document.createElement("div");
            div.className = "list-item";
            div.innerHTML = `<strong>${c.nome}</strong><br><small>${c.descrizione || ''}</small>`;
            div.onclick = () => selectCassetto(c.id);
            list.appendChild(div);
        });

        const select = document.getElementById("cassetto-select");
        select.innerHTML = '<option value="">Seleziona cassetto</option>';
        cassetti.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.id;
            opt.textContent = c.nome;
            select.appendChild(opt);
        });
    } catch (e) {
        console.error("Errore loadCassetti:", e);
    }
}

function selectCassetto(id) {
    current_cassetto_id = id;
    loadBilanci(id);
}

function showNewCassetto() {
    const nome = prompt("Nome cassetto:");
    if (!nome) return;

    fetch(`/api/cassetti?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome_cliente: nome, descrizione: "" })
    })
    .then(r => r.json())
    .then(d => {
        if (d.success) loadCassetti();
    })
    .catch(e => alert("Errore: " + e.message));
}

// ============================================================================
// BILANCI
// ============================================================================

async function loadBilanci(cassetto_id) {
    try {
        const res = await fetch(`/api/bilanci/${cassetto_id}?token=${token}`);
        const data = await res.json();
        bilanci = data;
        
        const list = document.getElementById("bilanci-list");
        list.innerHTML = "";
        bilanci.forEach(b => {
            const div = document.createElement("div");
            div.className = "list-item";
            div.innerHTML = `<strong>Anno ${b.anno}</strong><br><small>${b.file_path}</small>`;
            div.onclick = () => runAnalisi(b.id);
            list.appendChild(div);
        });
    } catch (e) {
        console.error("Errore loadBilanci:", e);
    }
}

async function uploadBilancio() {
    const cassetto_id = document.getElementById("cassetto-select").value;
    const anno = document.getElementById("anno").value;
    const file = document.getElementById("bilancio-file").files[0];

    if (!cassetto_id || !anno || !file) {
        alert("Compila tutti i campi");
        return;
    }

    const formData = new FormData();
    formData.append("cassetto_id", cassetto_id);
    formData.append("anno", anno);
    formData.append("file", file);
    formData.append("token", token);

    try {
        const res = await fetch("/api/bilanci/upload", {
            method: "POST",
            body: formData
        });

        if (res.ok) {
            alert("Upload completato");
            loadBilanci(cassetto_id);
            document.getElementById("bilancio-file").value = "";
            document.getElementById("anno").value = "";
        } else {
            alert("Errore upload");
        }
    } catch (e) {
        alert("Errore: " + e.message);
    }
}

// ============================================================================
// ANALISI
// ============================================================================

async function runAnalisi(bilancio_id) {
    showScreen("analisi-screen");
    
    document.getElementById("analisi-narrativa").innerHTML = '<div class="loading">Analizzando...</div>';
    document.getElementById("capsule-list").innerHTML = '';

    try {
        const res = await fetch(`/api/analisi/${bilancio_id}?token=${token}`, {
            method: "POST"
        });

        const result = await res.json();
        
        document.getElementById("analisi-narrativa").textContent = result.narrativa;

        const capsuleList = document.getElementById("capsule-list");
        capsuleList.innerHTML = "";
        result.capsule.forEach(cap => {
            const card = document.createElement("div");
            card.className = "capsula-card";
            card.innerHTML = `
                <h4>${cap.tipo}</h4>
                <div class="meta">
                    Carica: ${(cap.carica * 100).toFixed(0)}% | 
                    Timeline: ${cap.timeline_days} giorni
                </div>
                <p>${cap.narrativa}</p>
                <p><strong>Azioni:</strong> ${cap.azioni}</p>
            `;
            capsuleList.appendChild(card);
        });
    } catch (e) {
        document.getElementById("analisi-narrativa").innerHTML = `<p style="color:red;">Errore: ${e.message}</p>`;
    }
}

function backToDashboard() {
    showScreen("dashboard");
}

// ============================================================================
// INIT
// ============================================================================

window.addEventListener("load", () => {
    if (token) {
        showScreen("dashboard");
        loadCassetti();
    } else {
        showScreen("login-screen");
    }
});
