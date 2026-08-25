/**
 * dashboard.js
 * Fetches aggregate stats from get_predictions.php and renders
 * stat cards + two Chart.js charts + the at-risk student table.
 */

renderSidebar("dashboard.html");

async function loadDashboard() {
    try {
        const data = await api("get_predictions.php");

        document.getElementById("statTotal").textContent = data.total_students;
        document.getElementById("statHigh").textContent = data.performance_distribution.Good;
        document.getElementById("statAverage").textContent = data.performance_distribution.Average;
        document.getElementById("statAtRisk").textContent =
            data.risk_distribution.HIGH + data.risk_distribution.MEDIUM;
        document.getElementById("avgAttendanceNote").textContent =
            `Average attendance: ${data.average_attendance}%`;

        // Performance distribution chart
        new Chart(document.getElementById("perfChart"), {
            type: "bar",
            data: {
                labels: ["Good", "Average", "Poor"],
                datasets: [{
                    label: "Students",
                    data: [
                        data.performance_distribution.Good,
                        data.performance_distribution.Average,
                        data.performance_distribution.Poor,
                    ],
                    backgroundColor: ["#0EA894", "#E2A63B", "#E1524F"],
                    borderRadius: 8,
                }],
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });

        // Cluster distribution chart
        new Chart(document.getElementById("clusterChart"), {
            type: "doughnut",
            data: {
                labels: ["High Performer", "Average Performer", "At-Risk Student"],
                datasets: [{
                    data: [
                        data.cluster_distribution["High Performer"],
                        data.cluster_distribution["Average Performer"],
                        data.cluster_distribution["At-Risk Student"],
                    ],
                    backgroundColor: ["#0EA894", "#3454D1", "#E1524F"],
                }],
            },
            options: { plugins: { legend: { position: "bottom" } } },
        });

        // At-risk table
        const tbody = document.getElementById("atRiskTableBody");
        if (data.at_risk_students.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="muted">No at-risk students yet — run some predictions first.</td></tr>`;
        } else {
            tbody.innerHTML = data.at_risk_students.map(s => `
                <tr>
                    <td class="mono">${s.roll_number}</td>
                    <td>${s.name}</td>
                    <td>${s.final_prediction}</td>
                    <td>${riskBadge(s.risk_level)}</td>
                    <td class="muted small">${new Date(s.prediction_date).toLocaleString()}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        if (!guardAuth(err)) {
            document.getElementById("atRiskTableBody").innerHTML =
                `<tr><td colspan="5" class="error-msg" style="display:block;">${err.message}</td></tr>`;
        }
    }
}

loadDashboard();
