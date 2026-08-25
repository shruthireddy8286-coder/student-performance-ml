/**
 * whatif.js
 * Renders 8 sliders (one per feature), and on every change (debounced)
 * calls simulate.php -> Flask /predict directly, with NO student_id
 * and NO database write. Pure exploration tool.
 */

renderSidebar("whatif.html");

const SLIDERS = [
    { key: "attendance", label: "Attendance (%)", min: 0, max: 100, step: 1, start: 75 },
    { key: "assignment_score", label: "Assignment Score", min: 0, max: 100, step: 1, start: 70 },
    { key: "internal_marks", label: "Internal Exam Marks", min: 0, max: 100, step: 1, start: 65 },
    { key: "previous_semester_marks", label: "Previous Semester Marks", min: 0, max: 100, step: 1, start: 65 },
    { key: "study_hours", label: "Study Hours / Day", min: 0, max: 10, step: 0.5, start: 2.5 },
    { key: "quiz_score", label: "Quiz Score", min: 0, max: 100, step: 1, start: 65 },
    { key: "participation", label: "Class Participation", min: 0, max: 100, step: 1, start: 60 },
    { key: "assignment_completion", label: "Assignment Completion (%)", min: 0, max: 100, step: 1, start: 70 },
];

const wrap = document.getElementById("slidersWrap");
wrap.innerHTML = SLIDERS.map(s => `
    <div class="slider-row">
        <div class="slider-label">
            <span>${s.label}</span>
            <span class="slider-value" id="val-${s.key}">${s.start}</span>
        </div>
        <input type="range" id="slider-${s.key}" min="${s.min}" max="${s.max}" step="${s.step}" value="${s.start}">
    </div>
`).join("");

function getCurrentValues() {
    const values = {};
    SLIDERS.forEach(s => {
        values[s.key] = parseFloat(document.getElementById(`slider-${s.key}`).value);
    });
    return values;
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

let debounceTimer = null;
async function runSimulation() {
    const resultWrap = document.getElementById("liveResult");
    try {
        const r = await api("simulate.php", { method: "POST", body: getCurrentValues() });
        resultWrap.innerHTML = `
            <div class="flex gap-8" style="margin-bottom:14px;">
                <span class="badge ${r.risk_level.toLowerCase()}">${r.risk_level} RISK</span>
                <strong>${r.final_prediction}</strong>
            </div>
            ${probBar("Good", r.good_probability, "#0EA894")}
            ${probBar("Average", r.average_probability, "#E2A63B")}
            ${probBar("Poor", r.poor_probability, "#E1524F")}
            <p class="small muted mt-24">Cluster: <strong>${r.cluster_name}</strong></p>
            <p class="small muted">Random Forest: ${r.supervised_prediction} · ANN: ${r.ann_prediction}</p>
        `;
    } catch (err) {
        if (!guardAuth(err)) {
            resultWrap.innerHTML = `<div class="error-msg" style="display:block;">${err.message}</div>`;
        }
    }
}

SLIDERS.forEach(s => {
    const slider = document.getElementById(`slider-${s.key}`);
    slider.addEventListener("input", () => {
        document.getElementById(`val-${s.key}`).textContent = slider.value;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runSimulation, 350); // debounce so we don't spam the API
    });
});

// Run once on load with the starting values
runSimulation();
