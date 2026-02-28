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


  user: Mapped["User"] = relationship("User", back_populates="sessions")