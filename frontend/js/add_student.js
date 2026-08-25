/**
 * add_student.js
 * Step 1: create the student profile (add_student.php)
 * Step 2: unlock and submit the academic data form (save_performance.php)
 */

renderSidebar("add_student.html");

let currentStudentId = null;

document.getElementById("studentForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        roll_number: document.getElementById("roll_number").value.trim(),
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        department: document.getElementById("department").value.trim(),
        year: document.getElementById("year").value,
        section: document.getElementById("section").value.trim(),
    };
    try {
        const data = await api("add_student.php", { method: "POST", body: payload });
        currentStudentId = data.student_id;

        // Unlock the performance data form
        const perfCard = document.getElementById("perfCard");
        perfCard.style.opacity = "1";
        perfCard.querySelectorAll("input, button").forEach(el => el.disabled = false);
        perfCard.querySelector("p").textContent = `Enter academic data for this student (ID #${currentStudentId}).`;
    } catch (err) {
        if (!guardAuth(err)) alert(err.message);
    }
});

document.getElementById("perfForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentStudentId) return;

    const fields = ["attendance", "assignment_score", "internal_marks", "previous_semester_marks",
                     "study_hours", "quiz_score", "participation", "assignment_completion"];
    const payload = { student_id: currentStudentId };
    for (const f of fields) payload[f] = document.getElementById(f).value;

    try {
        await api("save_performance.php", { method: "POST", body: payload });
        alert("Academic data saved. You can now run a prediction from the Students page.");
        window.location.href = `prediction.html?student_id=${currentStudentId}`;
    } catch (err) {
        if (!guardAuth(err)) alert(err.message);
    }
});
