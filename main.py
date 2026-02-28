from flask import Flask , render_template , request , url_for , redirect
from models import (db , User , Role)
from sqlalchemy import (select)
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, current_user



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
    role_names = ['admin' , 'provider' , 'patient']

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
            username = "superuser",
            email = "superuser@ltu.ac.uk",
            password = "abc", # later get from .env for security
            role=admin_role
        )
        db.session.add(super_user)
        print(f"Superuser created.")

    db.session.commit()

# forms
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

# routes

# default page -> go to self registraton user
@app.route("/" , methods=["GET" , "POST"])
def register_user():
    if request.method == "POST":
        form = RegistrationForm(request.form)        
        if form.validate_on_submit():
           # role must exist and user must be authenticated if role is not patient
            if form.role.data not in ["admin", "provider", "patient"]:
                return render_template('register-user.html' , form=form , errors=["Invalid role"])
            # user must be authenticated if role is not patient
            if not current_user.is_authenticated and form.role.data in ["admin", "provider"]:
                return render_template('register-user.html' , form=form , errors=["User must be authenticated"])

            # Look up Role by name
            role = db.session.scalar(select(Role).where(Role.name == form.role.data))
            if not role:
                return render_template('register-user.html', form=form, errors=["Invalid role"])

            # register the user(patient,admin,provider)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('register-user.html' , form=form , errors=form.errors)
    
    return render_template('register-user.html' , form=RegistrationForm())

@app.route("/login" , methods=["GET" , "POST"])
def login():
    return render_template('login.html')

@app.route("/dashboard" , methods=["GET"])
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
