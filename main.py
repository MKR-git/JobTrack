from datetime import date
import sqlite3

conn = sqlite3.connect("jobtrack.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    role TEXT,
    location TEXT,
    status TEXT,
    salary TEXT,
    applied_date TEXT
)
""")

conn.commit()
jobs = [
    {
        "company": "HCLTech",
        "role": "Python Developer",
        "location": "Bangalore",
        "status": "Applied",
        "salary": "5 LPA",
        "applied_date": "2026-09-25"
    },
    {
        "company": "TCS",
        "role": "Python Developer",
        "location": "Bangalore",
        "status": "Interview",
        "salary": "4 LPA",
        "applied_date": "2026-09-25"
    }
]
for job in jobs:
    existing = cursor.execute(
        "SELECT id FROM jobs WHERE company = ?",
        (job["company"],)
    ).fetchone()

    if existing is None:
        cursor.execute("""
        INSERT INTO jobs (company, role, location, status, salary, applied_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job["company"],
            job["role"],
            job["location"],
            job["status"],
            job["salary"],
            job["applied_date"]
        ))

conn.commit()

rows = cursor.execute("""
SELECT company, role, location, status, salary, applied_date
FROM jobs
""").fetchall()

jobs = []

for row in rows:
    jobs.append({
        "company": row[0],
        "role": row[1],
        "location": row[2],
        "status": row[3],
        "salary": row[4],
        "applied_date": row[5]
    })

def add_job():
    company = input("Enter company name: ")
    role = input("Enter job role: ")
    location = input("Enter location: ")

    print("1. Applied")
    print("2. Interview")
    print("3. Selected")
    print("4. Rejected")

    status_choice = input("Enter status choice: ")
    if status_choice == "1":
        status = "Applied"
    elif status_choice == "2":
        status = "Interview"
    elif status_choice == "3":
        status = "Selected"
    elif status_choice == "4":
        status = "Rejected"
    else:
        print("Invalid status choice")
        return

    salary = input("Enter salary: ")
    applied_date = str(date.today())


    new_job = {
        "company": company,
        "role": role,
        "location": location,
        "status": status,
        "salary": salary,
        "applied_date": applied_date
    }

    jobs.append(new_job)
    cursor.execute("""
    INSERT INTO jobs (company, role, location, status, salary, applied_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        company,
        role,
        location,
        status,
        salary,
        str(applied_date)
    ))

    conn.commit()




def view_jobs():
    if len(jobs) == 0:
        print("No job applications found.")
        return
    print("Total Jobs:", len(jobs))
    print("\nJob Applications:")

    for i, job in enumerate(jobs, start=1):
        print("Job", i)
        print("--------------------")
        print("Company:", job["company"])
        print("Role:", job["role"])
        print("Location:", job["location"])
        print("Status:", job["status"])
        print("Salary:", job["salary"])
        print("Applied Date:", job["applied_date"])


def search_job():
    search = input("Enter company name or job role to search: ")
    found = 0
    for job in jobs:
        if search.lower() in job["company"].lower() or search.lower() in job["role"].lower():
            found += 1
            print("\nJob Found:")
            print("Company:", job["company"])
            print("Role:", job["role"])
            print("Location:", job["location"])
            print("Status:", job["status"])
            print("Salary:", job["salary"])
            print("Applied Date:", job["applied_date"])

    if found == 0:
        print("Job not found")
    else:
        print("\nTotal Jobs Found:", found)


def delete_job():
    company = input("Enter company name to delete: ")

    for job in jobs:
        if job["company"].lower() == company.lower():
            confirm = input("Are you sure you want to delete this job? (yes/no): ")

            if confirm.lower() == "yes":
                jobs.remove(job)

                cursor.execute(
                    "DELETE FROM jobs WHERE company = ?",
                    (company,)
                )

                conn.commit()

                print("Job deleted successfully")
            else:
                print("Deletion cancelled")

            return

    print("Job not found")


def update_status():
    company = input("Enter company name: ")

    for job in jobs:
        if job["company"].lower() == company.lower():
            print("Current Status:", job["status"])
            print("1. Applied")
            print("2. Interview")
            print("3. Selected")
            print("4. Rejected")

            status_choice = input("Enter status choice: ")
            confirm = input("Are you sure you want to update the status? (yes/no): ")

            if confirm.lower() != "yes":
                print("Status update cancelled")
                return
            if status_choice == "1":
                new_status = "Applied"
            elif status_choice == "2":
                new_status = "Interview"
            elif status_choice == "3":
                new_status = "Selected"
            elif status_choice == "4":
                new_status = "Rejected"
            else:
                print("Invalid status choice")
                return
            job["status"] = new_status
            cursor.execute(
                "UPDATE jobs SET status = ? WHERE LOWER(company) = LOWER(?)",
                (new_status, company)
            )

            conn.commit()
            print(job["company"], "status updated successfully")
            return

    print("Job not found")


def show_status_summary():
    applied = 0
    interview = 0
    selected = 0
    rejected = 0

    for job in jobs:
        if job["status"].lower() == "applied":
            applied += 1
        elif job["status"].lower() == "interview":
            interview += 1
        elif job["status"].lower() == "selected":
            selected += 1
        elif job["status"].lower() == "rejected":
            rejected += 1

    print("\n===== Status Summary =====")
    print("Applied:", applied)
    print("Interview:", interview)
    print("Selected:", selected)
    print("Rejected:", rejected)



while True:
    print("\n========== JOBTRACK ==========")
    print("Job Application Management System")
    print("Total Applications:", len(jobs))
    print("1. Add Job")
    print("2. View Jobs")
    print("3. Search Job")
    print("4. Delete Job")
    print("5. Update Status")
    print("6. Status Summary")
    print("7. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_job()
    elif choice == "2":
        view_jobs()
    elif choice == "3":
        search_job()
    elif choice == "4":
        delete_job()
    elif choice == "5":
        update_status()
    elif choice == "6":
        show_status_summary()
    elif choice == "7":
        print("Thank you for using JobTrack")
        break

    conn.close()