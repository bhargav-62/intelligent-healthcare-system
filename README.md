
<<<<<<< HEAD
# MediCare AI — Personalized Healthcare & Medicine Recommendation System

An educational healthcare AI prototype that explores symptom patterns using a machine-learning classifier and a Flask web application.

> **Medical disclaimer:** This project is for educational and demonstration purposes only. It is not clinically validated and must not be used to diagnose diseases, recommend medicines, or make treatment decisions.

## Project Overview

MediCare AI allows users to select symptoms through a web interface and view the output of a baseline Random Forest classifier trained on an educational symptom dataset.

The application demonstrates machine-learning integration, REST API development, input validation, automated testing, and frontend/backend communication.

## Features

- Searchable checklist of 132 symptom features.
- Random Forest baseline classification across 41 dataset labels.
- Flask API for prediction requests.
- Input validation for empty, malformed, and unknown symptoms.
- Health-check and model-information endpoints.
- Display of the leading model outputs and relative model scores.
- Responsive HTML, CSS, and JavaScript interface.
- Automated API tests using Python's `unittest` framework.
- Safety notices explaining the limitations of the model.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Data processing | Pandas, NumPy |
| Machine learning | Scikit-learn, Random Forest |
| Model persistence | Joblib |
| API testing | Flask test client, unittest |

## Project Structure

```text
medicare/
├── app.py
├── test_app.py
├── requirements.txt
├── .gitignore
├── README.md
├── models/
│   └── baseline_symptom_model.joblib
├── data/
│   ├── raw/
│   └── processed/
│       ├── unique_symptom_patterns.csv
│       ├── exploratory_dataset.csv
│       ├── symptom_dataset_report.json
│       ├── preparation_report.json
│       └── baseline_model_report.json
├── templates/
│   ├── index.html
│   ├── about.html
│   └── contact.html
├── train_baseline.py
├── evaluate_baseline.py
├── compare_models.py
├── clean_symptom_dataset.py
├── diagnose_symptom_data.py
├── dataset_quality_check.py
├── prepare_dataset.py
└── audit_project.py
```

The structure above describes the intended organization. Some files may be omitted from a shared repository depending on dataset permissions, file sizes, and sharing requirements.

## Requirements

- Python installed on your system.
- pip package installer.
- A terminal such as Command Prompt or the VS Code terminal.

## Installation

### 1. Clone the repository

After publishing the project to GitHub, use:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd medicare
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
=======
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
>>>>>>> 646a0fa42de3d14d52ec70924008488bf5a6704b
```

### 3. Install dependencies

```bash
<<<<<<< HEAD
python -m pip install -r requirements.txt
```

### 4. Check the model file

Ensure the trained model exists at:

```text
models/baseline_symptom_model.joblib
```

The web application loads this saved model. Run the training script only if you need to regenerate the model and have the required training data available.

### 5. Start the application
=======
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
>>>>>>> 646a0fa42de3d14d52ec70924008488bf5a6704b

```bash
python app.py
```

<<<<<<< HEAD
Open the following URL in your browser:

```text
http://127.0.0.1:5000/
```

## API Endpoints

### Homepage

```http
GET /
```

Returns the web interface.

### Health check

```http
GET /health
```

Reports whether the model loaded and how many symptom features are available.

### Model information

```http
GET /models
```

Returns information about the configured baseline model.

### Prediction

```http
POST /predict
Content-Type: application/json
```

Example request:

```json
{
  "symptoms": ["itching", "skin_rash"]
}
```

The symptom names must match the model's feature names exactly.

A successful response contains an educational prediction, leading model scores, selected symptoms, a timestamp, and a safety disclaimer.

An empty symptom list or an unknown feature is rejected with an HTTP 400 response.

## Model Evaluation

The current saved evaluation report records the following results:

| Metric | Recorded result |
|---|---:|
| Model | RandomForestClassifier |
| Distinct records after deduplication | 304 |
| Dataset classes | 41 |
| Symptom features | 132 |
| Holdout validation accuracy | 100% |
| Holdout macro F1 | 1.00 |
| Five-fold cross-validation mean accuracy | 100% |
| Five-fold cross-validation mean macro F1 | 1.00 |

These are results from the current educational dataset and evaluation procedure. They must not be interpreted as evidence of clinical accuracy.

### Dataset Limitations

- Deduplication leaves only 304 distinct symptom patterns.
- Individual disease classes contain very few distinct patterns.
- The dataset has not been clinically validated.
- The unusually high evaluation scores require further investigation.
- Performance on these data does not establish generalization to real patients.

A more rigorous evaluation would require appropriately sourced, clinically reviewed data and an independent evaluation design.

## Automated Testing

Run the application tests from the project directory:

```bash
python -m unittest test_app -v
```

The current test suite contains eight tests covering:

- Homepage loading.
- Health endpoint.
- Model information endpoint.
- Valid prediction requests.
- Empty symptom rejection.
- Invalid request formats.
- Unknown symptom rejection.

The latest reported run passed all eight tests. Run the command again after code changes to verify the current state.

## Safety and Privacy

- This application is an educational prototype, not a medical device.
- Predictions are not diagnoses.
- Relative model scores are not calibrated clinical probabilities.
- Do not use the output to select medicines or determine treatment.
- Seek qualified medical care for health concerns and urgent care for severe or rapidly worsening symptoms.
- Do not submit real patient information to a public demonstration.
- Before deployment, review logging, data retention, access controls, security settings, and applicable privacy requirements.

## Future Improvements

- Investigate the unusually high validation scores.
- Improve dataset provenance and evaluation methodology.
- Add automated tests for additional error conditions.
- Improve accessibility and mobile usability.
- Add clear model versioning and reproducible training instructions.
- Deploy only after security, privacy, and safety reviews.

## Author

Developed as an educational healthcare AI project associated with internship learning and development.

## License

Add a license only after deciding which license applies to your code and confirming that you have permission to redistribute the datasets and other project assets.
```

## Step 2 — Save and verify

Save the file with `Ctrl + S`, then run:

```bat
cd /d D:\medicare
dir README.md
```

## Step 3 — Next milestone: GitHub preparation 🚀

Once you've saved the README, we'll inspect your Git status and prepare the repository carefully. We should **not upload the full datasets or model files blindly**; we'll check their size and redistribution permissions first.

Send me **“done”** after saving the README, and we'll continue with the next step.
=======
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
>>>>>>> 646a0fa42de3d14d52ec70924008488bf5a6704b
