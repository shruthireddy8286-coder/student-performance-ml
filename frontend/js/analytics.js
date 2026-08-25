/**
 * analytics.js
 * Renders risk-level and cluster-distribution charts, plus the full
 * at-risk student table, using the same get_predictions.php summary
 * endpoint as the dashboard.
 */

renderSidebar("analytics.html");

async function loadAnalytics() {
    try {
        const data = await api("get_predictions.php");

        new Chart(document.getElementById("riskChart"), {
            type: "pie",
            data: {
                labels: ["Low Risk", "Medium Risk", "High Risk"],
                datasets: [{
                    data: [data.risk_distribution.LOW, data.risk_distribution.MEDIUM, data.risk_distribution.HIGH],
                    backgroundColor: ["#0EA894", "#E2A63B", "#E1524F"],
                }],
            },
            options: { plugins: { legend: { position: "bottom" } } },
        });

        new Chart(document.getElementById("clusterChart2"), {
            type: "bar",
            data: {
                labels: ["High Performer", "Average Performer", "At-Risk Student"],
                datasets: [{
                    data: [
                        data.cluster_distribution["High Performer"],
                        data.cluster_distribution["Average Performer"],
                        data.cluster_distribution["At-Risk Student"],
                    ],
                    backgroundColor: ["#0EA894", "#3454D1", "#E1524F"],
                    borderRadius: 8,
                }],
            },
            options: {
                indexAxis: "y",
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });

        const tbody = document.getElementById("analyticsTableBody");
        if (data.at_risk_students.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="muted">No at-risk students yet.</td></tr>`;
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
            document.getElementById("analyticsTableBody").innerHTML =
                `<tr><td colspan="5" class="error-msg" style="display:block;">${err.message}</td></tr>`;
        }
    }
}

loadAnalytics();
