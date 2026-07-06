from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ---------------- STORE DATA ----------------
attendance_data = {}
absent_data = {}

# ---------------- EMAIL SETTINGS ----------------
SENDER_EMAIL = "G-NTTF0824005@nttf.co.in"      # FROM (unchanged)
SENDER_PASSWORD = "P@ssw0rd"         # unchanged
PRINCIPAL_EMAIL = "G-NTTF0824019@nttf.co.in"    # TO

# 🔹 ADDED (ONLY ADDITION – does not change logic)
DISPLAY_NAME = "G-NTTF Attendance System"
REPLY_TO_EMAIL = "G-NTTF0824005@nttf.co.in"
CC_EMAIL = "G-NTTF0824005@nttf.co.in"

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- SUBMIT ATTENDANCE ----------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    date = data["date"]
    attendance = data["attendance"]

    absent_students = []
    for student, status in attendance.items():
        if status == "Absent":
            absent_students.append(student)

    attendance_data[date] = attendance
    absent_data[date] = absent_students

    return jsonify({"message": "Attendance saved successfully"})

# ---------------- ABSENT LETTER ----------------
@app.route("/absent_letter")
def absent_letter():
    date = request.args.get("date")
    return render_template(
        "absent.html",
        date=date,
        absent_students=absent_data.get(date, [])
    )

# ---------------- SEND MAIL ----------------
@app.route("/send_mail", methods=["POST"])
def send_mail():
    data = request.json
    date = data["date"]
    absentees = absent_data.get(date, [])

    subject = f"Absent Students Report - {date}"

    body = f"""To,
The Principal,
G-NTTF

Respected Sir,

The following trainees are absent today ({date}):

"""

    if absentees:
        for s in absentees:
            body += f"- {s}\n"
    else:
        body += "All students are present."

    body += "\n\nRegards,\nG-NTTF Attendance System"

    try:
        msg = MIMEMultipart()

        # ✅ ADDED (display name only)
        msg["From"] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"

        # existing behavior (unchanged)
        msg["To"] = PRINCIPAL_EMAIL

        # ✅ ADDED (safe headers)
        msg["Reply-To"] = REPLY_TO_EMAIL
        msg["Cc"] = CC_EMAIL

        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # ✅ ADDED (CC delivery only)
        server.sendmail(
            SENDER_EMAIL,
            [PRINCIPAL_EMAIL, CC_EMAIL],
            msg.as_string()
        )

        server.quit()

        return jsonify({"message": "Mail sent successfully to Principal ✅"})

    except Exception as e:
        return jsonify({"message": f"Mail failed ❌ {str(e)}"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
