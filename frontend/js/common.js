/**
 * common.js
 * Shared helpers used across every page: API base URL, fetch wrapper,
 * and the sidebar navigation markup.
 */

// Change this if your PHP backend lives somewhere else under WAMP.
// Default assumes: C:\wamp64\www\Student-Performance-ML\backend\
const API_BASE = "http://localhost/Student-Performance-ML/backend";

/**
 * Wrapper around fetch() that always sends/receives JSON and
 * includes cookies (needed for PHP session login).
 */
async function api(path, options = {}) {
    const res = await fetch(`${API_BASE}/${path}`, {
        method: options.method || "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        throw new Error(data.error || `Request failed (${res.status})`);
    }
    return data;
}

/** Applies the saved dark-mode preference immediately (call at top of every page). */
function applySavedTheme() {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }
}
applySavedTheme();

/** Injects the sidebar nav into any element with id="sidebar". */
function renderSidebar(activePage) {
    const el = document.getElementById("sidebar");
    if (!el) return;
    const links = [
        ["dashboard.html", "Dashboard"],
        ["students.html", "Students"],
        ["add_student.html", "Add Student"],
        ["bulk_upload.html", "Bulk Upload"],
        ["prediction.html", "Predict Performance"],
        ["whatif.html", "What-If Simulator"],
        ["analytics.html", "Analytics"],
        ["section_comparison.html", "Section Comparison"],
    ];
    const isDark = localStorage.getItem("theme") === "dark";
    el.innerHTML = `
        <div class="brand"><span class="dot"></span> Student ML Analytics</div>
        <nav>
            ${links.map(([href, label]) => `
                <a href="${href}" class="${activePage === href ? "active" : ""}">${label}</a>
            `).join("")}
            <a href="#" id="logoutLink">Log out</a>
        </nav>
        <div class="theme-toggle" id="themeToggle">
            <span id="themeIcon">${isDark ? "☀️" : "🌙"}</span>
            <span id="themeLabel">${isDark ? "Light mode" : "Dark mode"}</span>
        </div>
        <div class="footer-note">Signed in as <strong id="sidebarUser">...</strong></div>
    `;

    document.getElementById("logoutLink").addEventListener("click", async (e) => {
        e.preventDefault();
        try { await api("logout.php", { method: "POST", body: {} }); } catch (_) {}
        window.location.href = "login.html";
    });

    document.getElementById("themeToggle").addEventListener("click", () => {
        const nowDark = document.body.classList.toggle("dark-mode");
        localStorage.setItem("theme", nowDark ? "dark" : "light");
        document.getElementById("themeIcon").textContent = nowDark ? "☀️" : "🌙";
        document.getElementById("themeLabel").textContent = nowDark ? "Light mode" : "Dark mode";
    });

    const nameEl = document.getElementById("sidebarUser");
    if (nameEl) nameEl.textContent = sessionStorage.getItem("username") || "Teacher";
}

/** Redirect to login.html if a protected-page fetch returns 401. */
function guardAuth(err) {
    if (String(err.message).toLowerCase().includes("not authenticated")) {
        window.location.href = "login.html";
        return true;
    }
    return false;
}

function riskBadge(level) {
    const cls = (level || "").toLowerCase();
    return `<span class="badge ${cls}">${level || "-"}</span>`;
}
