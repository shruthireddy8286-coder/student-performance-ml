/**
 * bulk_upload.js
 * Parses a teacher-uploaded CSV client-side with PapaParse, then loops
 * through each row calling add_student.php + save_performance.php —
 * no new backend endpoint needed, reuses the existing single-student ones.
 */

renderSidebar("bulk_upload.html");

const REQUIRED_COLUMNS = [
    "roll_number", "name", "email", "department", "year", "section",
    "attendance", "assignment_score", "internal_marks", "previous_semester_marks",
    "study_hours", "quiz_score", "participation", "assignment_completion",
];

let parsedRows = [];

document.getElementById("downloadSampleBtn").addEventListener("click", () => {
    const sample =
        REQUIRED_COLUMNS.join(",") + "\n" +
        "201,Sample Student,sample@example.com,CSE,2,A,85,80,78,75,3,82,80,90\n";
    const blob = new Blob([sample], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample_students.csv";
    a.click();
    URL.revokeObjectURL(url);
});

document.getElementById("csvFile").addEventListener("change", (e) => {
    const file = e.target.files[0];
    const errorEl = document.getElementById("uploadError");
    errorEl.style.display = "none";
    document.getElementById("uploadBtn").disabled = true;
    if (!file) return;

    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
            const headers = results.meta.fields || [];
            const missing = REQUIRED_COLUMNS.filter(c => !headers.includes(c));
            if (missing.length > 0) {
                errorEl.textContent = `CSV is missing required columns: ${missing.join(", ")}`;
                errorEl.style.display = "block";
                return;
            }
            parsedRows = results.data;
            document.getElementById("uploadBtn").disabled = false;
            errorEl.style.display = "none";
        },
        error: (err) => {
            errorEl.textContent = "Could not parse CSV: " + err.message;
            errorEl.style.display = "block";
        },
    });
});

document.getElementById("uploadBtn").addEventListener("click", async () => {
    if (parsedRows.length === 0) return;

    const progressWrap = document.getElementById("progressWrap");
    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");
    const resultsWrap = document.getElementById("resultsWrap");
    const resultsBody = document.getElementById("resultsTableBody");

    progressWrap.classList.remove("hidden");
    resultsWrap.classList.remove("hidden");
    resultsBody.innerHTML = "";
    document.getElementById("uploadBtn").disabled = true;

    let successCount = 0;

    for (let i = 0; i < parsedRows.length; i++) {
        const row = parsedRows[i];
        const pct = Math.round(((i + 1) / parsedRows.length) * 100);
        progressBar.style.width = pct + "%";
        progressText.textContent = `Uploading ${i + 1} of ${parsedRows.length}…`;

        try {
            const studentPayload = {
                roll_number: row.roll_number?.trim(),
                name: row.name?.trim(),
                email: row.email?.trim() || "",
                department: row.department?.trim() || "",
                year: row.year || "",
                section: row.section?.trim() || "",
            };
            const studentRes = await api("add_student.php", { method: "POST", body: studentPayload });
            const studentId = studentRes.student_id;

            const perfPayload = { student_id: studentId };
            for (const f of ["attendance", "assignment_score", "internal_marks", "previous_semester_marks",
                             "study_hours", "quiz_score", "participation", "assignment_completion"]) {
                perfPayload[f] = row[f];
            }
            await api("save_performance.php", { method: "POST", body: perfPayload });

            successCount++;
            resultsBody.innerHTML += `
                <tr><td>${i + 1}</td><td>${row.name}</td>
                    <td><span class="badge low">Added</span></td></tr>`;
        } catch (err) {
            resultsBody.innerHTML += `
                <tr><td>${i + 1}</td><td>${row.name || "-"}</td>
                    <td><span class="badge high">Failed: ${err.message}</span></td></tr>`;
        }
    }

    progressText.textContent = `Done — ${successCount} of ${parsedRows.length} students added successfully.`;
    document.getElementById("uploadBtn").disabled = false;
});
