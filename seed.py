from __future__ import annotations

from sqlalchemy import select
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

from models import db, User, Role, MedicalRecord


load_dotenv()

DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")


def seed_database(app):
    with app.app_context():
        db.create_all()

        # create roles if not created
        role_names = ["admin", "provider", "patient"]

        for r in role_names:
            existing_role = db.session.scalars(
                select(Role).where(Role.name == r)
            ).first()

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
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=admin_role,
            )
            db.session.add(super_user)
            print("Superuser created.")

        # if initial seed patients do not exist then create them
        if not db.session.scalar(
            select(User).where(User.email == "patient1@ltu.ac.uk")
        ):
            # create some dummy users, multiple patients and one provider
            patient1 = User(
                username="patient1",
                email="patient1@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient1)
            print("Patient 1 created.")

            patient2 = User(
                username="patient2",
                email="patient2@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient2)
            print("Patient 2 created.")

            patient3 = User(
                username="patient3",
                email="patient3@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient3)
            print("Patient 3 created.")

            patient4 = User(
                username="patient4",
                email="patient4@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient4)
            print("Patient 4 created.")

            patient5 = User(
                username="patient5",
                email="patient5@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient5)
            print("Patient 5 created.")

            patient6 = User(
                username="patient6",
                email="patient6@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient6)
            print("Patient 6 created.")

            patient7 = User(
                username="patient7",
                email="patient7@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient7)
            print("Patient 7 created.")

            patient8 = User(
                username="patient8",
                email="patient8@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient8)
            print("Patient 8 created.")

            patient9 = User(
                username="patient9",
                email="patient9@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient9)
            print("Patient 9 created.")

            patient10 = User(
                username="patient10",
                email="patient10@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "patient")),
            )
            db.session.add(patient10)
            print("Patient 10 created.")

            provider = User(
                username="provider",
                email="provider@ltu.ac.uk",
                password=generate_password_hash(DEFAULT_USER_PASSWORD),
                role=db.session.scalar(select(Role).where(Role.name == "provider")),
            )
            db.session.add(provider)
            print("Provider created.")

            # Make sure to flush so that patients get their IDs
            db.session.flush()

            # create some dummy medical records for the patients
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
                user=patient1,
            )
            db.session.add(medical_record1)
            print("Medical record 1 created.")

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
                user=patient1,
            )
            db.session.add(medical_record2)
            print("Medical record 2 created.")

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
                user=patient1,
            )
            db.session.add(medical_record3)
            print("Medical record 3 created.")

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
                user=patient1,
            )
            db.session.add(medical_record4)
            print("Medical record 4 created.")

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
                user=patient2,
            )
            db.session.add(medical_record5)
            print("Medical record 5 created.")

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
                user=patient1,
            )
            db.session.add(medical_record6)
            print("Medical record 6 created.")

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
                user=patient1,
            )
            db.session.add(medical_record7)
            print("Medical record 7 created.")

            medical_record8 = MedicalRecord(
                age=57,
                sex="Female",
                dataset="Cleveland",
                cp="asymptomatic",
                trestbps=120,
                chol=354,
                fbs=False,
                restecg="normal",
                thalach=163,
                user=patient2,
            )
            db.session.add(medical_record8)
            print("Medical record 8 created.")

            medical_record9 = MedicalRecord(
                age=63,
                sex="Male",
                dataset="Cleveland",
                cp="asymptomatic",
                trestbps=130,
                chol=254,
                fbs=False,
                restecg="lv hypertrophy",
                thalach=147,
                user=patient3,
            )
            db.session.add(medical_record9)
            print("Medical record 9 created.")

            medical_record10 = MedicalRecord(
                age=53,
                sex="Male",
                dataset="Cleveland",
                cp="asymptomatic",
                trestbps=140,
                chol=203,
                fbs=True,
                restecg="lv hypertrophy",
                thalach=155,
                user=patient4,
            )
            db.session.add(medical_record10)
            print("Medical record 10 created.")

        db.session.commit()

