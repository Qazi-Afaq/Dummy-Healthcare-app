# Secure Patient Management System (SPMS)

This is a web based patient management system for a private healthcare provider. This applications allows clinicians and adminstrators to create , read, update/ and delete patient medical records. Patients can also view their own medical records.
Patients can self register while admins and providers must be registered by administrators.

The system uses a dual database design:
SQLITE for user data, authentication and medical records and mongodb for prescriptions and appointments with access filtered by role/identity.

-- SETUP:
1. clone this repository from github
2. Create virtual enviornment using command "python3 -m venv .venv"
3. use command "pip install -r requirements.txt" to install the required packages.
4. A .env file is required to avoid hardcoding passwords and sensitive information.
5. run the application with command "flask --app main run"

-- ENVIRONMENT VARIABLES
SECRET_KEY : Flask secret key used by flask for sessions and CSRF
DATABASE_URL: The main Sqlite database url to connect to the database
MONGODB_URI: Connection string to connect to mongodb instance.
MONGODB_DB_NAME:  MongoDB database name assessment-1-db
MONGODB_APPOINTMENTS_COLLECTION: Appointments collection name appointments`
MONGODB_PRESCRIPTIONS_COLLECTION:  Prescriptions collection name prescriptions`
DEFAULT_USER_PASSWORD: Password for seeded users (change in production)

-- Project structure
main.py: Flask app, routes, forms, and integration with SQLite and MongoDB.
models.py: SQLAlchemy models (User, Role, MedicalRecord).
forms.py: Flask-WTF forms to be rendered on front-end and validated.
seed.py: For pre-populating database on executions where the database is empty.
templates/: Jinja2 HTML templates.
static/: CSS and static assets.
tests/: Unit and integration tests.
requirements.txt: Python dependencies.

