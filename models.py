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
    auth_sessions = relationship("AuthSession", back_populates="user", lazy="selectin")

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'status': self.status,
            'create_date': self.create_date.strftime('%d/%m/%Y %H:%M:%S')
        }


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="auth_sessions")
    token = Column(String)
    status = Column(String, default='active')
    create_date = Column(DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'status': self.status,
            'create_date': self.create_date.strftime('%d/%m/%Y %H:%M:%S')
        }


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    name = Column(String)
    locale = Column(String, default='RU')
    max_players = Column(Integer, default=1000)
    status = Column(String, default='active')
    create_date = Column(DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'name': self.name,
            'locale': self.locale,
            'max_players': self.max_players,
            'status': self.status,
            'create_date': self.create_date.strftime('%d/%m/%Y %H:%M:%S')
        }