from flask import Flask , render_template , request , url_for , redirect
from models import (db , User , Role , MedicalRecord)
from sqlalchemy import (select)
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from seed import seed_database

from forms import (
    RegistrationForm,
    LoginForm,
    MedicalRecordForm
)

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "assessment-1-db")
MONGODB_APPOINTMENTS_COLLECTION = os.getenv("MONGODB_APPOINTMENTS_COLLECTION", "appointments")
MONGODB_PRESCRIPTIONS_COLLECTION = os.getenv("MONGODB_PRESCRIPTIONS_COLLECTION", "prescriptions")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI environment variable is not set")

# Mongodatabase connection
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB_NAME]
appointments_collection = mongo_db[MONGODB_APPOINTMENTS_COLLECTION]
prescriptions_collection = mongo_db[MONGODB_PRESCRIPTIONS_COLLECTION]
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
db.init_app(app)

# initialize and seed the database
seed_database(app)



# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None





# =============================== Routes ===============================

# admins that register users
@app.route("/register-user" , methods=["GET" , "POST"])
@login_required
def register_user():

    # user must be authenticated and an admin :
    if not current_user.is_authenticated or current_user.role.name != "admin":
        return  render_template('404.html' , errors={"error": ["User must be authenticated and an admin to do this action"]})


    if request.method == "POST":
        form = RegistrationForm(request.form)        
        if form.validate_on_submit():
            # user must be authenticated and an admin
            if not current_user.is_authenticated or current_user.role.name != "admin":
                return render_template('register-user.html' , form=form , errors={"error": ["User must be authenticated and an admin to do this action"]})

            # Look up Role by name
            role = db.session.scalar(select(Role).where(Role.name == form.role.data))
            if not role:
                return render_template('register-user.html', form=form, errors={"error": ["Invalid role"]})

            # register the user(patient,admin,provider)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('register-user.html' , form=form , errors=form.errors)
    
    return render_template('register-user.html' , form=RegistrationForm())

# register patient for unauthenticated users or users who are not logged in
@app.route("/self-register-patient" , methods=["GET" , "POST"])
def self_register_patient():
    # if current user is authenticated redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        form = RegistrationForm(request.form)
        if form.validate_on_submit():
            # role must be patient
            if not form.role.data == "patient":
                return render_template('self-register-patient.html' , form=form , errors={"error": ["Role must be patient"]})

            # register the patient
            new_patient = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role=db.session.scalar(select(Role).where(Role.name == "patient"))
            )
            db.session.add(new_patient)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('self-register-patient.html' , form=form , errors=form.errors)
    return render_template('self-register-patient.html' , form=RegistrationForm())

@app.route("/login" , methods=["GET" , "POST"])
def login():

    # if current user is authenticated then redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        form = LoginForm(request.form)
        if form.validate_on_submit():
            user = db.session.scalar(select(User).where(User.email == form.email.data))
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('login.html' , form=form , errors={"error": ["Invalid email or password"]})
        else:
            return render_template('login.html' , form=form , errors=form.errors)
    return render_template('login.html' , form=LoginForm())

@app.route("/logout" , methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/" , methods=["GET"])
@login_required
def home():
    # if current user is a patient then show the patient home page with all their medical records
    if current_user.role.name == "patient":
        medical_records = db.session.scalars(select(MedicalRecord).where(MedicalRecord.user_id == current_user.id)).all()
        return render_template('home.html' , medical_records=medical_records)
    # else get the medical records of all the users and show them on home page
    medical_records = db.session.scalars(select(MedicalRecord)).all()
    return render_template('home.html' , medical_records=medical_records)

# add a medical record of a patient
@app.route("/add-medical-record" , methods=["GET" , "POST"])
@login_required
def add_medical_record():

    if current_user.role.name not in ["admin", "provider"]:
        # render custom html saying role must be admin or provider
        return "<h1>Role must be admin or provider</h1>"

    if request.method == "POST":
        form = MedicalRecordForm(request.form)
        if form.validate_on_submit():
            # add the medical record
            patient = db.session.scalar(select(User).where(User.email == form.patient_email.data))
            if not patient:
                return render_template('add-medical-record.html' , form=form , errors={"error": ["Patient not found"]})
            new_medical_record = MedicalRecord(
                user_id=patient.id,
                age=form.age.data,
                sex=form.sex.data,
                dataset=form.dataset.data,
                cp=form.cp.data,
                trestbps=form.trestbps.data,
                chol=form.chol.data,
                fbs=form.fbs.data,
                restecg=form.restecg.data,
                thalach=form.thalach.data,
            )
            db.session.add(new_medical_record)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('add-medical-record.html' , form=form , errors=form.errors)
    return render_template('add-medical-record.html' , form=MedicalRecordForm())

# edit medical record
@app.route("/edit-medical-record/<int:medical_record_id>" , methods=["GET" , "POST"])
@login_required
def edit_medical_record(medical_record_id):
    # role of curreent user must be admin
    if current_user.role.name != "admin":
        # render custom html saying role must be admin
        return "<h1>Role must be admin</h1>"

    # POST METHOD: edit the medical record
    if request.method == "POST":
        form = MedicalRecordForm(request.form)
        if form.validate_on_submit():
            # edit the medical record
            medical_record = db.session.get(MedicalRecord, medical_record_id)
            if not medical_record:
                 return render_template('404.html' , errors={"error": ["Medical record not found"]})
            medical_record.age = form.age.data
            medical_record.sex = form.sex.data
            medical_record.dataset = form.dataset.data
            medical_record.cp = form.cp.data
            medical_record.trestbps = form.trestbps.data
            medical_record.chol = form.chol.data
            medical_record.fbs = form.fbs.data
            medical_record.restecg = form.restecg.data
            medical_record.thalach = form.thalach.data
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('404.html' , errors=form.errors)

    # GET METHOD: return edit-medical-record html with the medical record filled in the form
    medical_record = db.session.get(MedicalRecord, medical_record_id)
    if not medical_record:
        return render_template('404.html' , errors={"error": ["Medical record not found"]})
    return render_template('edit-medical-record.html' , form=MedicalRecordForm(obj=medical_record) , medical_record=medical_record)


# delete medical record
@app.route("/delete-medical-record/<int:medical_record_id>" , methods=["GET"])
@login_required
def delete_medical_record(medical_record_id):
    # role of curreent user must be admin
    if current_user.role.name != "admin":
        # render custom html saying role must be admin
        return "<h1>Role must be admin</h1>"
    
    # delete the medical record
    medical_record = db.session.get(MedicalRecord, medical_record_id)
    if not medical_record:
        return render_template('404.html' , errors={"error": ["Medical record not found"]})
    db.session.delete(medical_record)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/prescriptions", methods=["GET"])
@login_required
def prescriptions():

    # patient only sees their prescriptions
    if current_user.role.name == "patient":
        prescriptions = list(
            prescriptions_collection.find(
                {"patient_email": current_user.email}
            )
        )
    else:
        prescriptions = list(prescriptions_collection.find())

    return render_template(
        "prescriptions.html",
        prescriptions=prescriptions
    )

@app.route("/appointments", methods=["GET"])
@login_required
def appointments():

    # if patient → only see their appointments
    if current_user.role.name == "patient":
        appointments = list(
            appointments_collection.find(
                {"patient_email": current_user.email}
            )
        )
    else:
        appointments = list(appointments_collection.find())

    return render_template(
        "appointments.html",
        appointments=appointments
    )

if __name__ == "__main__":
    app.run(debug=True)
