import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from typing import List

class RepoStatus(enum.Enum):
    private = 1
    public = 2

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    email = Column(String(255), unique=True, nullable=True)
    access_token = Column(String(255))

    repos: Mapped[List["Repo"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Repo(Base):
    __tablename__ = "repos"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(Enum(RepoStatus))
    stars = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user: Mapped["User"] = relationship(back_populates="repos")
