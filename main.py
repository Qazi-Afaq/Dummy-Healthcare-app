from flask import Flask , render_template , request , url_for , redirect
from models import (db , User , Role , MedicalRecord)
from sqlalchemy import (select)
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField, IntegerField
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient

# Mongodatabase connection
mongo_client = MongoClient("mongodb+srv://afaq2qazi_db_user:mongodb@cluster0.tjbgjyz.mongodb.net/") # later from .env
mongo_db = mongo_client["assessment-1-db"]
appointments_collection = mongo_db["appointments"]
prescriptions_collection = mongo_db["prescriptions"]


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "get_from_env_later"
db.init_app(app)



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


# create pre seeded roles and superuser
with app.app_context():
    db.create_all()

    # create roles if not created
    role_names = ['admin', 'provider', 'patient']

    for r in role_names:
        existing_role = db.session.scalars(select(Role).where(Role.name == r)).first()

        if not existing_role:
            new_role = Role(name=r)
            db.session.add(new_role)
            print(f"Created new role {r}")

    # if superuser does not exist then create one
    if not db.session.scalar(select(User).where(User.role.has(name="admin"))):
        # get role where name is admin
        admin_role = db.session.scalar(select(Role).where(Role.name == "admin"))
        super_user = User(
            username="superuser",
            email="superuser@ltu.ac.uk",
            password=generate_password_hash("Testtest1"),  # later get from .env for security
            role=admin_role
        )
        db.session.add(super_user)
        print(f"Superuser created.")

    # if "patient1@ltu.ac.uk" does not exist then create it
    if not db.session.scalar(select(User).where(User.email == "patient1@ltu.ac.uk")):
        # create some dummy users, two patients and one provider
        patient1 = User(
            username="patient1",
            email="patient1@ltu.ac.uk",
            password=generate_password_hash("Testtest1"),
            role=db.session.scalar(select(Role).where(Role.name == "patient"))
        )
        db.session.add(patient1)
        print(f"Patient 1 created.")

        patient2 = User(
            username="patient2",
            email="patient2@ltu.ac.uk",
            password=generate_password_hash("Testtest1"),
            role=db.session.scalar(select(Role).where(Role.name == "patient"))
        )
        db.session.add(patient2)
        print(f"Patient 2 created.")

        provider = User(
            username="provider",
            email="provider@ltu.ac.uk",
            password=generate_password_hash("Testtest1"),
            role=db.session.scalar(select(Role).where(Role.name == "provider"))
        )
        db.session.add(provider)
        print(f"Provider created.")

        # Make sure to flush so that patient1 and patient2 get their IDs
        db.session.flush()

        # we create some dummy medical records for the two patients from any combinations of the values below
        """
        id,age,sex,dataset,cp,trestbps,chol,fbs,restecg,thalch,exang,oldpeak,slope,ca,thal,num
        1,63,Male,Cleveland,typical angina,145,233,TRUE,lv hypertrophy,150,FALSE,2.3,downsloping,0,fixed defect,0
        2,67,Male,Cleveland,asymptomatic,160,286,FALSE,lv hypertrophy,108,TRUE,1.5,flat,3,normal,2
        3,67,Male,Cleveland,asymptomatic,120,229,FALSE,lv hypertrophy,129,TRUE,2.6,flat,2,reversable defect,1
        4,37,Male,Cleveland,non-anginal,130,250,FALSE,normal,187,FALSE,3.5,downsloping,0,normal,0
        5,41,Female,Cleveland,atypical angina,130,204,FALSE,lv hypertrophy,172,FALSE,1.4,upsloping,0,normal,0
        6,56,Male,Cleveland,atypical angina,120,236,FALSE,normal,178,FALSE,0.8,upsloping,0,normal,0
        7,62,Female,Cleveland,asymptomatic,140,268,FALSE,lv hypertrophy,160,FALSE,3.6,downsloping,2,normal,3
        8,57,Female,Cleveland,asymptomatic,120,354,FALSE,normal,163,TRUE,0.6,upsloping,0,normal,0
        9,63,Male,Cleveland,asymptomatic,130,254,FALSE,lv hypertrophy,147,FALSE,1.4,flat,1,reversable defect,2
        10,53,Male,Cleveland,asymptomatic,140,203,TRUE,lv hypertrophy,155,TRUE,3.1,downsloping,0,reversable defect,1
        11,57,Male,Cleveland,asymptomatic,140,192,FALSE,normal,148,FALSE,0.4,flat,0,fixed defect,0
        12,56,Female,Cleveland,atypical angina,140,294,FALSE,lv hypertrophy,153,FALSE,1.3,flat,0,normal,0
        13,56,Male,Cleveland,non-anginal,130,256,TRUE,lv hypertrophy,142,TRUE,0.6,flat,1,fixed defect,2
        14,44,Male,Cleveland,atypical angina,120,263,FALSE,normal,173,FALSE,0,upsloping,0,reversable defect,0
        15,52,Male,Cleveland,non-anginal,172,199,TRUE,normal,162,FALSE,0.5,upsloping,0,reversable defect,0
        """

        medical_record1 = MedicalRecord(
            age=63,
            sex="Male",
            dataset="Cleveland",
            cp="typical angina",
            trestbps=145,
            chol=233,
            fbs=True,
            restecg="lv hypertrophy",
            thalach=150,
            user=patient1
        )
        db.session.add(medical_record1)
        print(f"Medical record 1 created.")

        medical_record2 = MedicalRecord(
            age=67,
            sex="Male",
            dataset="Cleveland",
            cp="asymptomatic",
            trestbps=160,
            chol=286,
            fbs=False,
            restecg="lv hypertrophy",
            thalach=108,
            user=patient1
        )
        db.session.add(medical_record2)
        print(f"Medical record 2 created.")

        medical_record3 = MedicalRecord(
            age=67,
            sex="Male",
            dataset="Cleveland",
            cp="asymptomatic",
            trestbps=120,
            chol=229,
            fbs=False,
            restecg="lv hypertrophy",
            thalach=129,
            user=patient1
        )
        db.session.add(medical_record3)
        print(f"Medical record 3 created.")

        medical_record4 = MedicalRecord(
            age=37,
            sex="Male",
            dataset="Cleveland",
            cp="non-anginal",
            trestbps=130,
            chol=250,
            fbs=False,
            restecg="normal",
            thalach=187,
            user=patient1
        )
        db.session.add(medical_record4)
        print(f"Medical record 4 created.")

        medical_record5 = MedicalRecord(
            age=41,
            sex="Female",
            dataset="Cleveland",
            cp="atypical angina",
            trestbps=130,
            chol=204,
            fbs=False,
            restecg="lv hypertrophy",
            thalach=172,
            user=patient2
        )
        db.session.add(medical_record5)
        print(f"Medical record 5 created.")

        medical_record6 = MedicalRecord(
            age=56,
            sex="Male",
            dataset="Cleveland",
            cp="atypical angina",
            trestbps=120,
            chol=236,
            fbs=False,
            restecg="normal",
            thalach=178,
            user=patient1
        )
        db.session.add(medical_record6)
        print(f"Medical record 6 created.")

        medical_record7 = MedicalRecord(
            age=62,
            sex="Female",
            dataset="Cleveland",
            cp="asymptomatic",
            trestbps=140,
            chol=268,
            fbs=False,
            restecg="lv hypertrophy",
            thalach=160,
            user=patient1
        )
        db.session.add(medical_record7)
        print(f"Medical record 7 created.")

    db.session.commit()

# =============================== Forms ===============================
from wtforms import ValidationError
import re

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            validators.DataRequired(),
            validators.Length(min=3, max=25)
        ]
    )
    email = StringField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Length(min=6, max=35),
            validators.Email(message="Invalid email format")
        ]
    )
    password = PasswordField(
        'New Password',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Repeat Password')
    role = SelectField(
        'Role',
        choices=[('admin', 'Admin'), ('provider', 'Provider'), ('patient', 'Patient')]
    )
    submit = SubmitField('Register')

    # validate email uniqueness
    def validate_email(self, field):
        if db.session.scalar(select(User).where(User.email == field.data)):
            raise ValidationError("Email already exists.")

    # Custom validation for username
    def validate_username(self, field):
        if not field.data.isalnum():
            raise ValidationError("Username must be alphanumeric.")

    # Custom validation for password complexity
    def validate_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number.")

class LoginForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Length(min=6, max=35),
            validators.Email(message="Invalid email format")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired(),
            validators.Length(min=8, max=25)
        ]
    )
    submit = SubmitField('Login')

from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField, validators
from flask_wtf import FlaskForm

class MedicalRecordForm(FlaskForm):
    patient_email = StringField(
        'Patient Email',
        validators=[validators.DataRequired(), validators.Email(message="Invalid email format")]
    )
    age = IntegerField(
        'Age',
        validators=[validators.DataRequired(), validators.NumberRange(min=0, max=100)]
    )
    sex = SelectField(
        'Sex',
        choices=[('Male', 'Male'), ('Female', 'Female')],
        validators=[validators.DataRequired()]
    )
    dataset = SelectField(
        'Dataset',
        choices=[('Cleveland', 'Cleveland'), ('Hungarian', 'Hungarian'), ('Switzerland', 'Switzerland')],
        validators=[validators.DataRequired()]
    )
    cp = SelectField(
        'CP',
        choices=[('typical angina', 'typical angina'), 
                 ('asymptomatic', 'asymptomatic'), 
                 ('non-anginal', 'non-anginal'), 
                 ('atypical angina', 'atypical angina')],
        validators=[validators.DataRequired()]
    )

    # nullable fields
    trestbps = IntegerField('Trestbps')   
    chol = IntegerField('Chol')           
    fbs = BooleanField('FBS')             
    restecg = SelectField(
        'Restecg',
        choices=[('lv hypertrophy', 'lv hypertrophy'), ('normal', 'normal')]
    )                                     
    thalach = IntegerField('Thalach')     

    submit = SubmitField('Add Medical Record')

# =============================== Routes ===============================

# default page -> go to self registraton user
@app.route("/register-user" , methods=["GET" , "POST"])
def register_user():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == "POST":
        form = RegistrationForm(request.form)        
        if form.validate_on_submit():
            # user must be authenticated and an admin
            if current_user.is_authenticated and current_user.role.name == "admin":
                return render_template('register-user.html' , form=form , errors={"error": ["User must be authenticated and an admin"]})

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

    # role of curreent user must be admin
    if current_user.role.name != "admin":
        # render custom html saying role must be admin
        return "<h1>Role must be admin</h1>"

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
            return redirect(url_for('add_medical_record'))
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
