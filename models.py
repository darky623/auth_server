from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    user_hash = Column(String)
    status = Column(String, default='active')
    create_date = Column(DateTime)
    auth_sessions = relationship("AuthSession", back_populates="user")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="auth_sessions")
    token = Column(String)
    status = Column(String, default='active')
    create_date = Column(DateTime)


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    name = Column(String)
    locale = Column(String)
    max_players = Column(String)
    status = Column(String)
    create_date = Column(DateTime)
