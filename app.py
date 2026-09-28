from flask import Flask, render_template, request, redirect, Response, session, flash
from functools import wraps
import sqlite3
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "jobtrack-secret-key"


def get_db_connection():
    conn = sqlite3.connect("jobs.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_users_table():
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


create_users_table()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/register")

        if len(password) < 6:
            flash("Password must contain at least 6 characters", "error")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:

            conn.execute(
                """
                INSERT INTO users
                (username, password)
                VALUES (?, ?)
                """,
                (
                    username,
                    hashed_password
                )
            )

            conn.commit()
            conn.close()

            flash("Account created successfully. Please login.", "success")
            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            flash("Username already exists", "error")
            return redirect("/register")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Welcome to JobTrack!", "success")
            return redirect("/")

        flash("Invalid username or password", "error")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
@login_required
def home():

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE jobs
        SET user_id = ?
        WHERE user_id IS NULL
        """,
        (session["user_id"],)
    )

    conn.commit()

    total_jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    applied_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Applied", session["user_id"])
    ).fetchone()[0]

    interview_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Interview", session["user_id"])
    ).fetchone()[0]

    selected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Selected", session["user_id"])
    ).fetchone()[0]

    rejected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Rejected", session["user_id"])
    ).fetchone()[0]

    if total_jobs > 0:
        success_rate = (selected_jobs / total_jobs) * 100
    else:
        success_rate = 0

    location_jobs = conn.execute(
        """
        SELECT location, COUNT(*) AS count
        FROM jobs
        WHERE user_id = ?
        GROUP BY location
        ORDER BY count DESC
        """,
        (session["user_id"],)
    ).fetchall()

    role_jobs = conn.execute(
        """
        SELECT role, COUNT(*) AS count
        FROM jobs
        WHERE user_id = ?
        GROUP BY role
        ORDER BY count DESC
        """,
        (session["user_id"],)
    ).fetchall()

    company_jobs = conn.execute(
        """
        SELECT company, COUNT(*) AS count
        FROM jobs
        WHERE user_id = ?
        GROUP BY company
        ORDER BY count DESC
        """,
        (session["user_id"],)
    ).fetchall()

    recent_jobs = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE user_id = ?
        ORDER BY date_applied DESC
        LIMIT 5
        """,
        (session["user_id"],)
    ).fetchall()

    salary_stats = conn.execute(
        """
        SELECT
            MAX(
                CAST(
                    REPLACE(LOWER(salary), 'lpa', '')
                    AS REAL
                )
            ) AS highest,

            MIN(
                CAST(
                    REPLACE(LOWER(salary), 'lpa', '')
                    AS REAL
                )
            ) AS lowest,

            AVG(
                CAST(
                    REPLACE(LOWER(salary), 'lpa', '')
                    AS REAL
                )
            ) AS average

        FROM jobs
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "index.html",
        total_jobs=total_jobs,
        applied_jobs=applied_jobs,
        interview_jobs=interview_jobs,
        selected_jobs=selected_jobs,
        rejected_jobs=rejected_jobs,
        success_rate=success_rate,
        location_jobs=location_jobs,
        role_jobs=role_jobs,
        company_jobs=company_jobs,
        recent_jobs=recent_jobs,
        salary_stats=salary_stats
    )


@app.route("/profile")
@login_required
def profile():

    conn = get_db_connection()

    total_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    applied_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Applied", session["user_id"])
    ).fetchone()[0]

    interview_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Interview", session["user_id"])
    ).fetchone()[0]

    selected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Selected", session["user_id"])
    ).fetchone()[0]

    rejected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Rejected", session["user_id"])
    ).fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        username=session["username"],
        total_jobs=total_jobs,
        applied_jobs=applied_jobs,
        interview_jobs=interview_jobs,
        selected_jobs=selected_jobs,
        rejected_jobs=rejected_jobs
    )

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (session["user_id"],)
        ).fetchone()

        if not user:
            conn.close()
            return "User not found"

        if not check_password_hash(
            user["password"],
            current_password
        ):
            conn.close()
            return "Current password is incorrect"

        if len(new_password) < 6:
            conn.close()
            return "New password must contain at least 6 characters"

        if new_password != confirm_password:
            conn.close()
            return "New passwords do not match"

        hashed_password = generate_password_hash(
            new_password
        )

        conn.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                hashed_password,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Password changed successfully!", "success")

        return redirect("/profile")

    return render_template("change_password.html")


@app.route("/add-job", methods=["GET", "POST"])
@login_required
def add_job():

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        status = request.form["status"]
        salary = request.form["salary"]
        date_applied = request.form["date_applied"]

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO jobs
            (company, role, location, status, salary, date_applied, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                location,
                status,
                salary,
                date_applied,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/view-jobs")

    return render_template("add_job.html")


@app.route("/view-jobs")
@login_required
def view_jobs():

    status = request.args.get("status")
    search = request.args.get("search")
    location = request.args.get("location")
    role = request.args.get("role")
    company = request.args.get("company")
    sort = request.args.get("sort", "newest")

    page = request.args.get(
        "page",
        1,
        type=int
    )

    jobs_per_page = request.args.get(
        "per_page",
        5,
        type=int
    )

    if jobs_per_page not in [5, 10, 20]:
        jobs_per_page = 5

    if page < 1:
        page = 1

    conn = get_db_connection()

    total_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    if sort == "oldest":
        order_by = "date_applied ASC"
    else:
        order_by = "date_applied DESC"

    # Main jobs query
    query = """
        SELECT *
        FROM jobs
        WHERE user_id = ?
    """

    # Separate count query
    count_query = """
        SELECT COUNT(*)
        FROM jobs
        WHERE user_id = ?
    """

    parameters = [
        session["user_id"]
    ]

    count_parameters = [
        session["user_id"]
    ]

    # Search filter
    if search:

        query += """
            AND (
                company LIKE ?
                OR role LIKE ?
                OR location LIKE ?
            )
        """

        count_query += """
            AND (
                company LIKE ?
                OR role LIKE ?
                OR location LIKE ?
            )
        """

        search_value = "%" + search + "%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

        count_parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Status filter
    if status:

        query += """
            AND status = ?
        """

        count_query += """
            AND status = ?
        """

        parameters.append(status)
        count_parameters.append(status)

    # Location filter
    if location:

        query += """
            AND location = ?
        """

        count_query += """
            AND location = ?
        """

        parameters.append(location)
        count_parameters.append(location)

    # Role filter
    if role:

        query += """
            AND role = ?
        """

        count_query += """
            AND role = ?
        """

        parameters.append(role)
        count_parameters.append(role)

    # Company filter
    if company:

        query += """
            AND company = ?
        """

        count_query += """
            AND company = ?
        """

        parameters.append(company)
        count_parameters.append(company)

    # Count filtered jobs
    filtered_jobs = conn.execute(
        count_query,
        count_parameters
    ).fetchone()[0]

    total_pages = (
        filtered_jobs + jobs_per_page - 1
    ) // jobs_per_page

    if total_pages > 0 and page > total_pages:
        page = total_pages

    offset = (page - 1) * jobs_per_page

    # Sorting and pagination
    query += f"""
        ORDER BY {order_by}
        LIMIT ? OFFSET ?
    """

    parameters.extend([
        jobs_per_page,
        offset
    ])

    jobs = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    return render_template(
        "view_jobs.html",
        jobs=jobs,
        total_jobs=total_jobs,
        filtered_jobs=filtered_jobs,
        page=page,
        total_pages=total_pages,
        jobs_per_page=jobs_per_page,
        search=search,
        location=location,
        role=role,
        company=company,
        status=status,
        sort=sort
    )


@app.route("/export-jobs")
@login_required
def export_jobs():

    status = request.args.get("status")
    search = request.args.get("search")
    company = request.args.get("company")
    sort = request.args.get("sort", "newest")

    conn = get_db_connection()

    if sort == "oldest":
        order_by = "date_applied ASC"
    else:
        order_by = "date_applied DESC"

    query = """
        SELECT *
        FROM jobs
        WHERE user_id = ?
    """

    parameters = [session["user_id"]]

    if search:

        query += """
            AND (
                company LIKE ?
                OR role LIKE ?
                OR location LIKE ?
            )
        """

        search_value = "%" + search + "%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    if status:

        query += " AND status = ?"

        parameters.append(status)

    if company:

        query += " AND company = ?"

        parameters.append(company)

    query += f" ORDER BY {order_by}"

    jobs = conn.execute(
        query,
        parameters
    ).fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Company",
        "Role",
        "Location",
        "Status",
        "Salary",
        "Date Applied"
    ])

    for job in jobs:

        writer.writerow([
            job["id"],
            job["company"],
            job["role"],
            job["location"],
            job["status"],
            job["salary"],
            job["date_applied"]
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=jobtrack_jobs.csv"
    )

    return response


@app.route("/import-jobs", methods=["POST"])
@login_required
def import_jobs():

    file = request.files.get("csv_file")

    if not file or file.filename == "":
        return redirect("/view-jobs")

    try:

        file_content = file.stream.read().decode("utf-8-sig")

        csv_reader = csv.DictReader(
            io.StringIO(file_content)
        )

        conn = get_db_connection()

        for row in csv_reader:

            company = row.get("Company", "").strip()
            role = row.get("Role", "").strip()
            location = row.get("Location", "").strip()
            status = row.get("Status", "").strip()
            salary = row.get("Salary", "").strip()
            date_applied = row.get(
                "Date Applied",
                ""
            ).strip()

            if not company or not role:
                continue

            conn.execute(
                """
                INSERT INTO jobs
                (company, role, location, status, salary, date_applied, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company,
                    role,
                    location,
                    status,
                    salary,
                    date_applied,
                    session["user_id"]
                )
            )

        conn.commit()
        conn.close()

    except Exception as error:

        print("CSV import error:", error)

    return redirect("/view-jobs")


@app.route("/job/<int:job_id>")
@login_required
def job_details(job_id):

    conn = get_db_connection()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            session["user_id"]
        )
    ).fetchone()

    conn.close()

    return render_template(
        "job_details.html",
        job=job
    )


@app.route("/delete-job/<int:job_id>")
@login_required
def delete_job(job_id):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM jobs
        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Job deleted successfully!", "success")

    return redirect("/view-jobs")


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):

    conn = get_db_connection()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        AND user_id = ?
        """,
        (
            job_id,
            session["user_id"]
        )
    ).fetchone()

    if not job:
        conn.close()
        flash("Job not found.", "error")
        return redirect("/view-jobs")

    if request.method == "POST":

        company = request.form["company"].strip()
        role = request.form["role"].strip()
        location = request.form["location"].strip()
        status = request.form["status"].strip()
        salary = request.form["salary"].strip()
        date_applied = request.form["date_applied"].strip()

        if not company:
            conn.close()
            flash("Company name is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        if not role:
            conn.close()
            flash("Job role is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        if not location:
            conn.close()
            flash("Location is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        if not status:
            conn.close()
            flash("Application status is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        if not salary:
            conn.close()
            flash("Salary is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        if not date_applied:
            conn.close()
            flash("Application date is required.", "error")
            return redirect(f"/edit-job/{job_id}")

        conn.execute(
            """
            UPDATE jobs
            SET company = ?,
                role = ?,
                location = ?,
                status = ?,
                salary = ?,
                date_applied = ?
            WHERE id = ?
            AND user_id = ?
            """,
            (
                company,
                role,
                location,
                status,
                salary,
                date_applied,
                job_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Job updated successfully!", "success")

        return redirect("/view-jobs")

    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )


@app.route("/status-summary")
@login_required
def status_summary():

    conn = get_db_connection()

    applied_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Applied", session["user_id"])
    ).fetchone()[0]

    interview_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Interview", session["user_id"])
    ).fetchone()[0]

    selected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Selected", session["user_id"])
    ).fetchone()[0]

    rejected_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE status = ?
        AND user_id = ?
        """,
        ("Rejected", session["user_id"])
    ).fetchone()[0]

    conn.close()

    return render_template(
        "status_summary.html",
        applied_jobs=applied_jobs,
        interview_jobs=interview_jobs,
        selected_jobs=selected_jobs,
        rejected_jobs=rejected_jobs
    )


if __name__ == "__main__":
    app.run(debug=True)