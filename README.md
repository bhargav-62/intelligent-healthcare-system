
# MediCare AI 🏥

**An AI-Enabled Healthcare Management System Built with Flask and MySQL**

MediCare AI is a web-based healthcare management application that brings patient management, appointment scheduling, health records, and an experimental AI-powered symptom checker together in one dashboard.

The project combines a Flask backend, a MySQL database, and machine learning to demonstrate how healthcare workflows can be managed through a unified web application.

## ✨ Features

### 👥 Patient Management
- View and manage patient records.
- Add, update, retrieve, and delete patient information through the application APIs.
- Store patient details in MySQL.

### 📅 Appointment Management
- Schedule appointments for patients.
- View upcoming appointments.
- Update appointment details and status.
- Manage appointment records through Flask API endpoints.

### 🩺 Health Records
- Create and view health records.
- Update existing records and remove records when authorized.
- Store consultation and other health-record information in MySQL.

### 🤖 AI Symptom Checker
- Experimental machine-learning-based symptom analysis.
- Uses a trained model and symptom feature inputs.
- Loads the existing trained model instead of retraining it on every application start.
- Intended for educational demonstration, not medical diagnosis or treatment.

### 📊 Analytics and Reports
- View healthcare statistics derived from database records.
- Summarize patient, appointment, and health-record information.
- Generate report data and export supported reports as CSV.

### 🔐 Authentication
- Login and logout functionality.
- Session-based authentication.
- Production deployment requires complete authentication and authorization protection for all private pages and API endpoints.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL |
| Database Connectivity | PyMySQL |
| Frontend | HTML, CSS, JavaScript |
| Machine Learning | Scikit-learn |
| Model Persistence | Joblib / Pickle |
| Data Processing | Pandas, NumPy |
| Deployment Target | Render |
| Version Control | Git and GitHub |

## 🏗️ Project Structure

```text
medicare-ai/
├── app.py
├── db.py
├── create_admin.py
├── requirements.txt
├── .env
├── .gitignore
├── models/
│   └── baseline_symptom_model.joblib
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── patients.html
│   ├── appointments.html
│   ├── health_records.html
│   ├── analytics.html
│   ├── reports.html
│   └── symptom_checker.html
├── data/
├── backups/
└── README.md
```

*Note: This is an illustrative structure. Keep the actual filenames and model paths from your repository.*

## ⚙️ Prerequisites

Install the following before running the project:

- Python 3.10 or another version compatible with your installed dependencies.
- MySQL Server.
- MySQL Workbench (optional, for database management).
- Git.
- A code editor such as Visual Studio Code.

## 🚀 Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/medicare-ai.git
cd medicare-ai
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root.

Example configuration:

```env
FLASK_SECRET_KEY=replace_with_a_long_random_secret
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medicare_db
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
```

Use the exact variable names expected by your existing `app.py` and `db.py`. Never commit `.env` or expose database credentials in GitHub.

### 5. Configure the database

1. Start MySQL Server.
2. Create or select the `medicare_db` database.
3. Configure the database connection using your environment variables.
4. Ensure the required tables exist.
5. If restoring an existing backup, verify the destination database and backup before importing.

**Important:** Do not import a backup over an existing database without checking its contents first.

### 6. Run the application

```bash
python app.py
```

Open the local URL shown in the terminal, commonly:

```text
http://127.0.0.1:5000
```

## ☁️ Deployment

The planned deployment architecture uses:

- **GitHub** for source-code version control.
- **Render** to host the Flask application.
- **Managed MySQL** for the online database.

Typical Render configuration:

**Build command**
```bash
pip install -r requirements.txt
```

**Start command**
```bash
gunicorn app:app
```

Configure database connection variables and a strong `FLASK_SECRET_KEY` in the hosting provider's environment settings.

Before public deployment:
- Protect all patient, appointment, and health-record routes.
- Enforce authentication and role-based authorization.
- Enable secure session cookies over HTTPS.
- Restrict cross-origin access where appropriate.
- Keep database credentials and backups private.
- Test the deployed application and confirm that the existing model loads correctly.

Deployment is not considered complete until the hosted application and remote database have been tested.

## 🔒 Security and Privacy

- Never commit `.env`, database passwords, secret keys, or SQL backups.
- Use a dedicated database account with only the required privileges.
- Protect private records from unauthenticated and unauthorized requests.
- Back up the database before migrations and major changes.
- Use fictional data for demonstrations and development.

## ⚠️ Medical Disclaimer

MediCare AI is an educational software project. Its symptom checker is experimental and must not be used as a substitute for a qualified healthcare professional, medical diagnosis, emergency care, or treatment advice.

Do not use real patient information in a public demo unless the application has been appropriately secured and applicable privacy requirements have been addressed.

## 🎯 Project Objectives

- Develop a full-stack healthcare management application.
- Integrate Flask with a relational MySQL database.
- Implement patient, appointment, and health-record workflows.
- Demonstrate integration of a trained machine-learning model.
- Present database-driven analytics and reports.
- Prepare the application for secure cloud deployment.

## 🔮 Future Improvements

- Complete role-based access control.
- Add automated tests for authentication and API authorization.
- Improve audit logging and backup procedures.
- Add secure password-reset functionality.
- Add monitoring and production error reporting.
- Evaluate the symptom checker with appropriate validation and limitations.

## 👨‍💻 Author

**https://github.com/bhargav-62**

## 📄 License

Choose and add an appropriate open-source license before distributing this project publicly.
