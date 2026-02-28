from flask import Flask , render_template , request , url_for
from models import (db , User , Role)
from sqlalchemy import (select)
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField

from flask_login import LoginManager



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
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
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('provider', 'Provider'), ('patient', 'Patient')])
    confirm = PasswordField('Repeat Password')

# routes

# default page -> go to self registraton user
@app.route("/" , methods=["GET" , "POST"])
def register_user():
    return render_template('register-user.html')

if __name__ == "__main__":
    app.run(debug=True)
