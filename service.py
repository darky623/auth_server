import uuid
from datetime import datetime, timedelta

from database import UnitOfWork
from models import User, AuthSession, Server
from repository import UserNotFoundError
from utils import *


class Service:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, obj):
        raise NotImplementedError('Метод не переопределен')

    def get_by_id(self, _id: int):
        raise NotImplementedError('Метод не переопределен')

    def remove_by_id(self, _id: int):
        raise NotImplementedError('Метод не переопределен')


class UserService(Service):
    async def add(self, user_data):
        user_hash = get_user_hash({'username': user_data['username'], 'password': user_data['password']})
        async with self.uow.start() as uow_session:
            auth_session = AuthSession(token=str(uuid.uuid1()), create_date=datetime.now())
            user = User(email=user_data['email'],
                        username=user_data['username'],
                        user_hash=user_hash,
                        create_date=datetime.now())
            user.auth_sessions.append(auth_session)
            await uow_session.users.add(user)
            return auth_session.token

    async def get_by_id(self, _id: int) -> User:
        async with self.uow.start() as uow_session:
            return await uow_session.users.get_by_id(_id)

    async def get_user(self, **kwargs):
        async with self.uow.start() as uow_session:
            return await uow_session.users.get(**kwargs)

    async def remove_by_id(self, _id: int):
        async with self.uow.start() as uow_session:
            return await uow_session.users.remove_by_id(_id)

    async def remove(self, user: User):
        async with self.uow.start() as uow_session:
            return await uow_session.users.remove(user)

    async def verify_user_and_generate_token(self, user_data):
        async with self.uow.start() as uow_session:
            user = await self.validate_user(uow_session, user_data['username'], user_data['password'])
            return await self.generate_auth_token(user)

    async def validate_user(self, uow_session, username: str, password: str):
        user_hash = get_user_hash({"username": username, "password": password})
        try:
            user = await uow_session.users.get_by_hash(user_hash)
        except UserNotFoundError:
            raise CredentialsException('Неверные данные пользователя')
        return user

    async def generate_auth_token(self, user):
        auth_session = AuthSession(token=str(uuid.uuid1()), create_date=datetime.now())
        user.auth_sessions.append(auth_session)
        return auth_session.token

    async def check_token(self, token: str) -> bool:
        async with self.uow.start() as uow_session:
            auth_data = await uow_session.auth_sessions.get_token(token)
            if auth_data:
                if (datetime.now() - auth_data.create_date) <= timedelta(seconds=config.token_lifetime):
                    return True
                else:
                    auth_data.status = 'expired'
            return False




class ServerService(Service):
    async def add(self, server: Server):
        async with self.uow.start() as uow_session:
            await uow_session.servers.add(server)

    async def get_all(self) -> list[Server]:
        async with self.uow.start() as uow_session:
            return await uow_session.servers.get_all()


class CredentialsException(Exception):
    ...


class UserAlreadyExistsException(Exception):
    ...
