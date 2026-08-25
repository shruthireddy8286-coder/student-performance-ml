/**
 * prediction.js
 * Loads the student dropdown, calls predict.php, and renders the
 * result — including a hand-drawn semicircular risk gauge (SVG),
 * probability bars, model comparison and recommendations.
 */

renderSidebar("prediction.html");

const params = new URLSearchParams(window.location.search);
const preselectId = params.get("student_id");

async function loadStudents() {
    const select = document.getElementById("studentSelect");
    try {
        const data = await api("get_students.php");
        if (data.students.length === 0) {
            select.innerHTML = `<option value="">No students yet — add one first</option>`;
            return;
        }
        select.innerHTML = `<option value="">Choose a student…</option>` + data.students.map(s => `
            <option value="${s.student_id}" ${String(s.student_id) === preselectId ? "selected" : ""}>
                ${s.roll_number} — ${s.name}${s.attendance === null ? "  (no academic data yet)" : ""}
            </option>
        `).join("");
        document.getElementById("predictBtn").disabled = false;
    } catch (err) {
        if (!guardAuth(err)) select.innerHTML = `<option value="">Error loading students</option>`;
    }
}

/** Draws a semicircular risk gauge. value = poor_probability (0-100). */
function drawGauge(value, riskLevel) {
    const cx = 90, cy = 90, r = 70;
    const angleForValue = (v) => Math.PI - (v / 100) * Math.PI; // 180deg (0) -> 0deg (100)

    const arc = (startPct, endPct, color) => {
        const a1 = angleForValue(startPct), a2 = angleForValue(endPct);
        const x1 = cx + r * Math.cos(a1), y1 = cy - r * Math.sin(a1);
        const x2 = cx + r * Math.cos(a2), y2 = cy - r * Math.sin(a2);
        return `<path d="M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}" stroke="${color}" stroke-width="16" fill="none" stroke-linecap="round"/>`;
    };

    const needleAngle = angleForValue(value);
    const nx = cx + (r - 12) * Math.cos(needleAngle);
    const ny = cy - (r - 12) * Math.sin(needleAngle);

    const colorMap = { LOW: "#0EA894", MEDIUM: "#E2A63B", HIGH: "#E1524F" };
    const needleColor = colorMap[riskLevel] || "#171B2E";

    document.getElementById("gauge").innerHTML = `
        <svg viewBox="0 0 180 110" width="200" height="122">
            ${arc(0, 33.3, "#0EA894")}
            ${arc(33.3, 66.6, "#E2A63B")}
            ${arc(66.6, 100, "#E1524F")}
            <line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="${needleColor}" stroke-width="4" stroke-linecap="round"/>
            <circle cx="${cx}" cy="${cy}" r="6" fill="${needleColor}"/>
            <text x="${cx}" y="${cy + 26}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="#5A6076">
                Poor-risk ${value.toFixed(0)}%
            </text>
        </svg>
    `;
}

function probBar(label, pct, color) {
    return `
        <div style="margin-bottom:10px;">
            <div class="flex" style="justify-content:space-between;">
                <span class="small">${label}</span><span class="small mono">${pct}%</span>
            </div>
            <div style="background:#EEF1F8; border-radius:8px; height:9px; overflow:hidden;">
                <div style="width:${pct}%; background:${color}; height:100%;"></div>
            </div>
        </div>
    `;
}

document.getElementById("predictBtn").addEventListener("click", async () => {
    const studentId = document.getElementById("studentSelect").value;
    const errorEl = document.getElementById("predictError");
    errorEl.style.display = "none";
    if (!studentId) return;

    const btn = document.getElementById("predictBtn");
    btn.disabled = true;
    btn.textContent = "Predicting…";

    try {
        const r = await api("predict.php", { method: "POST", body: { student_id: studentId } });

        document.getElementById("resultSection").classList.remove("hidden");
        document.getElementById("predictionHeadline").textContent =
            `${r.student_name} (Roll No. ${r.roll_number})`;

        drawGauge(r.poor_probability, r.risk_level);
        document.getElementById("gaugeLabel").textContent = r.risk_level + " RISK";
        document.getElementById("gaugeSub").textContent =
            "Project-defined rule based on combined Poor-probability.";

        document.getElementById("probBars").innerHTML =
            probBar("Good", r.good_probability, "#0EA894") +
            probBar("Average", r.average_probability, "#E2A63B") +
            probBar("Poor", r.poor_probability, "#E1524F");

        document.getElementById("rfPred").textContent = r.supervised_prediction;
        document.getElementById("annPred").textContent = r.ann_prediction;
        document.getElementById("finalPred").textContent = r.final_prediction;
        document.getElementById("clusterName").textContent = r.cluster_name;

        document.getElementById("recommendList").innerHTML =
            r.recommendations.map(rec => `<li>${rec}</li>`).join("");

        document.getElementById("explanationList").innerHTML =
            (r.explanations || []).map(exp => `<li>${exp}</li>`).join("");

    } catch (err) {
        if (!guardAuth(err)) {
            errorEl.textContent = err.message;
            errorEl.style.display = "block";
        }
    } finally {
        btn.disabled = false;
        btn.textContent = "Predict Performance";
    }
});

document.getElementById("printBtn").addEventListener("click", () => {
    window.print();
});

loadStudents();
