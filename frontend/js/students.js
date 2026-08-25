/**
 * students.js
 * Loads the student list (with latest performance/prediction/cluster)
 * and supports search + delete + quick-link to Predict Performance page.
 */

renderSidebar("students.html");

async function loadStudents(search = "") {
    const tbody = document.getElementById("studentsTableBody");
    tbody.innerHTML = `<tr><td colspan="8" class="muted">Loading…</td></tr>`;
    try {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        const data = await api(`get_students.php${query}`);

        if (data.students.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="muted">No students found. <a href="add_student.html">Add one</a>.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.students.map(s => `
            <tr>
                <td class="mono">${s.roll_number}</td>
                <td>${s.name}</td>
                <td>${s.department || "-"}</td>
                <td>${s.attendance !== null ? s.attendance + "%" : "-"}</td>
                <td>${s.final_prediction || "<span class='muted'>Not predicted</span>"}</td>
                <td>${s.risk_level ? riskBadge(s.risk_level) : "-"}</td>
                <td>${s.cluster_name || "-"}</td>
                <td>
                    <a href="prediction.html?student_id=${s.student_id}" class="small">Predict</a>
                    &nbsp;·&nbsp;
                    <a href="student_detail.html?student_id=${s.student_id}" class="small">History</a>
                    &nbsp;·&nbsp;
                    <a href="#" class="small delete-link" data-id="${s.student_id}" style="color:var(--high);">Delete</a>
                </td>
            </tr>
        `).join("");

        document.querySelectorAll(".delete-link").forEach(link => {
            link.addEventListener("click", async (e) => {
                e.preventDefault();
                if (!confirm("Delete this student and all their records? This cannot be undone.")) return;
                try {
                    await api("delete_student.php", { method: "POST", body: { student_id: link.dataset.id } });
                    loadStudents(search);
                } catch (err) {
                    alert(err.message);
                }
            });
        });
    } catch (err) {
        if (!guardAuth(err)) {
            tbody.innerHTML = `<tr><td colspan="8" class="error-msg" style="display:block;">${err.message}</td></tr>`;
        }
    }
}

document.getElementById("searchBox").addEventListener("input", (e) => {
    clearTimeout(window._searchDebounce);
    window._searchDebounce = setTimeout(() => loadStudents(e.target.value.trim()), 300);
});

loadStudents();
