/**
 * student_detail.js
 * Loads one student's full prediction history (get_predictions.php?student_id=)
 * and renders a trend line chart of Poor-probability over time, plus a table.
 */

renderSidebar("students.html"); // keep "Students" highlighted since this is a drill-down

const params = new URLSearchParams(window.location.search);
const studentId = params.get("student_id");

async function loadHistory() {
    if (!studentId) {
        document.getElementById("historyTableBody").innerHTML =
            `<tr><td colspan="7" class="muted">No student selected.</td></tr>`;
        return;
    }
    try {
        const data = await api(`get_predictions.php?student_id=${studentId}`);
        const history = data.history || [];

        if (history.length === 0) {
            document.getElementById("studentTitle").textContent = "Student History";
            document.getElementById("historyTableBody").innerHTML =
                `<tr><td colspan="7" class="muted">No predictions yet for this student. Run one from the Prediction page.</td></tr>`;
            return;
        }

        document.getElementById("studentTitle").textContent =
            `${history[0].name} (Roll No. ${history[0].roll_number}) — History`;

        // History comes back newest-first; reverse for a left-to-right timeline
        const chronological = [...history].reverse();

        new Chart(document.getElementById("trendChart"), {
            type: "line",
            data: {
                labels: chronological.map(h => new Date(h.prediction_date).toLocaleDateString()),
                datasets: [{
                    label: "Poor-risk probability (%)",
                    data: chronological.map(h => h.poor_probability),
                    borderColor: "#E1524F",
                    backgroundColor: "rgba(225,82,79,0.08)",
                    fill: true,
                    tension: 0.3,
                }],
            },
            options: {
                scales: { y: { min: 0, max: 100 } },
                plugins: { legend: { display: false } },
            },
        });

        document.getElementById("historyTableBody").innerHTML = history.map(h => `
            <tr>
                <td class="small muted">${new Date(h.prediction_date).toLocaleString()}</td>
                <td>${h.final_prediction}</td>
                <td>${riskBadge(h.risk_level)}</td>
                <td class="mono">${h.good_probability}%</td>
                <td class="mono">${h.average_probability}%</td>
                <td class="mono">${h.poor_probability}%</td>
                <td>${h.cluster_name || "-"}</td>
            </tr>
        `).join("");

    } catch (err) {
        if (!guardAuth(err)) {
            document.getElementById("historyTableBody").innerHTML =
                `<tr><td colspan="7" class="error-msg" style="display:block;">${err.message}</td></tr>`;
        }
    }
}

loadHistory();
