/**
 * section_comparison.js
 * Loads department/section aggregate stats and renders a bar chart
 * of average Poor-risk probability per section, plus a full table.
 */

renderSidebar("section_comparison.html");

async function loadComparison() {
    const tbody = document.getElementById("sectionTableBody");
    try {
        const data = await api("get_section_comparison.php");
        const sections = (data.sections || []).filter(s => s.total_students > 0);

        if (sections.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="muted">No data yet — add students and run some predictions first.</td></tr>`;
            return;
        }

        const labels = sections.map(s => `${s.department || "—"} ${s.section || ""}`.trim());
        const avgPoor = sections.map(s => s.avg_poor_probability || 0);

        new Chart(document.getElementById("sectionChart"), {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Avg Poor-risk %",
                    data: avgPoor,
                    backgroundColor: avgPoor.map(v => v >= 40 ? "#E1524F" : v >= 20 ? "#E2A63B" : "#0EA894"),
                    borderRadius: 8,
                }],
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, max: 100 } },
            },
        });

        tbody.innerHTML = sections.map(s => `
            <tr>
                <td>${s.department || "-"}</td>
                <td>${s.section || "-"}</td>
                <td class="mono">${s.total_students}</td>
                <td class="mono">${s.good_count}</td>
                <td class="mono">${s.average_count}</td>
                <td class="mono">${s.poor_count}</td>
                <td class="mono">${s.high_risk_count}</td>
                <td class="mono">${s.avg_attendance !== null ? s.avg_attendance + "%" : "-"}</td>
            </tr>
        `).join("");
    } catch (err) {
        if (!guardAuth(err)) {
            tbody.innerHTML = `<tr><td colspan="8" class="error-msg" style="display:block;">${err.message}</td></tr>`;
        }
    }
}

loadComparison();
