from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    status = Column(String)
    reg_date = Column(DateTime)
    last_login = Column(DateTime)

