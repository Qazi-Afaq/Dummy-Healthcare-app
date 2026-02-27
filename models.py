from flask_sqlalchemy import SQLAlchemy
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
class User(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(nullable=False)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  role_id : Mapped[int] = mapped_column(ForeignKey("role.id"))
  
  role: Mapped["Role"] = relationship("Role", back_populates="users")

  sessions: Mapped[List["Session"]] = relationship("Session" , back_populates="user")

# Session
class Session(db.Model):
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  created_at: Mapped[datetime] = mapped_column(insert_default=func.now() , nullable=False)
  last_active: Mapped[datetime] = mapped_column(insert_default=func.now() , onupdate=func.now() , nullable=False)
  is_active: Mapped[bool] = mapped_column(default=True, nullable=False)  
  expires_at: Mapped[datetime] = mapped_column(
      nullable=False,
      default=lambda: datetime.now(tz=timezone.utc) + timedelta(hours=1)
  )
  session_token: Mapped[str] = mapped_column(String(128) , unique=True, nullable=False , default=lambda: secrets.token_hex(32))

  user: Mapped["User"] = relationship("User", back_populates="sessions")