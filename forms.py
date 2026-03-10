from wtforms import ValidationError
import re
from wtforms import BooleanField, StringField, PasswordField, validators, SelectField, SubmitField, IntegerField
from flask_wtf import FlaskForm
from models import (db , User)
from sqlalchemy import (select)



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
