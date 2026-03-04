from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import (
  DeclarativeBase,
  Mapped,
  mapped_column,
  relationship
)
from sqlalchemy import ForeignKey, String , func

from datetime import datetime , timedelta, timezone
from typing import List

import secrets

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

# Role
class Role(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(nullable=False)
  
  users: Mapped[List["User"]] = relationship("User", back_populates="role")


# User
class User(UserMixin, db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(nullable=False)
  email: Mapped[str] = mapped_column(String(128) , nullable=False , unique=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  role_id : Mapped[int] = mapped_column(ForeignKey("role.id"))
  
  role: Mapped["Role"] = relationship("Role", back_populates="users")

  medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="user")

# patient model based on following public dataset:
"""
id,age,sex,dataset,cp,trestbps,chol,fbs,restecg,thalch,exang,oldpeak,slope,ca,thal,num
1,63,Male,Cleveland,typical angina,145,233,TRUE,lv hypertrophy,150,FALSE,2.3,downsloping,0,fixed defect,0
2,67,Male,Cleveland,asymptomatic,160,286,FALSE,lv hypertrophy,108,TRUE,1.5,flat,3,normal,2
3,67,Male,Cleveland,asymptomatic,120,229,FALSE,lv hypertrophy,129,TRUE,2.6,flat,2,reversable defect,1
"""
class MedicalRecord(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  age: Mapped[int] = mapped_column(nullable=False)
  sex: Mapped[str] = mapped_column(nullable=False)
  dataset: Mapped[str] = mapped_column(nullable=False)
  cp: Mapped[str] = mapped_column(nullable=False)
  trestbps: Mapped[int] = mapped_column(nullable=True)
  chol: Mapped[int] = mapped_column(nullable=True)
  fbs: Mapped[bool] = mapped_column(nullable=True)
  restecg: Mapped[str] = mapped_column(nullable=True)
  thalach: Mapped[int] = mapped_column(nullable=True)

  user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  user: Mapped["User"] = relationship("User", back_populates="medical_records")