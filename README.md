# JobTrack – Python Full Stack Job Application Tracker

JobTrack is a Python Full Stack web application developed to manage and track job applications in one place.

## 🚀 Features

- User Registration and Login
- Secure Logout
- User-specific Job Data
- Add Job Applications
- View Job Applications
- Search Jobs by Company or Role
- Filter Jobs by Status
- Filter Jobs by Location
- Filter Jobs by Role
- Filter Jobs by Company
- Sort and Paginate Job Applications
- View Detailed Job Information
- Edit Job Applications
- Delete Job Applications with Confirmation
- Job Status Summary
- User Profile
- Change Password
- Flash Messages for User Actions
- SQLite Database

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja2

## 📂 Project Structure

```text
JobTrack/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── add_job.html
│   ├── change_password.html
│   ├── edit_job.html
│   ├── index.html
│   ├── job_details.html
│   ├── jobs.html
│   ├── login.html
│   ├── navbar.html
│   ├── profile.html
│   ├── register.html
│   ├── status_summary.html
│   └── view_jobs.html
│
├── app.py
├── create_db.py
├── main.py
├── .gitignore
└── README.md
