from sqlalchemy.future import select

from models import Base, User, Server, AuthSession
from sqlalchemy.ext.asyncio.session import AsyncSession


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_by_id(self, user_id: int):
        raise NotImplementedError("Метод не переопределен")

    def remove_by_id(self, _id: int):
        raise NotImplementedError("Метод не переопределен")

    def remove(self, model: Base):
        raise NotImplementedError("Метод не переопределен")

    def add(self, model: Base):
        raise NotImplementedError("Метод не переопределен")

    def get(self, **kwargs):
        raise NotImplementedError("Метод не переопределен")


class UserRepository(Repository):

    async def add(self, user: User):
        self.session.add(user)

    async def get_by_id(self, _id: int) -> User:
        stmt = select(User).filter_by(id=_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        if user:
            return user
        raise UserNotFoundError(_id)

    async def get_by_hash(self, user_hash):
        result = await self.session.execute(select(User).where(User.user_hash == user_hash))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError
        return user

    async def get(self, **kwargs):
        try:
            stmt = select(User).filter_by(**kwargs)
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            if user:
                return user
        except:
            raise UserNotFoundError()
        raise UserNotFoundError()

    async def remove_by_id(self, _id: int):
        user = await self.get_by_id(_id)
        return await self.session.delete(user)

    async def remove(self, user: User):
        return await self.session.delete(user)


class ServerRepository(Repository):
    async def add(self, server: Server):
        self.session.add(server)

    async def add_many(self, servers: list[Server]):
        self.session.add_all(servers)
        await self.session.flush()

    async def get(self, **kwargs) -> Server:
        try:
            stmt = select(Server).filter_by(**kwargs)
            result = await self.session.execute(stmt)
            server = result.scalars().first()
            if server:
                return server
        except:
            raise ServerNotFoundError()
        raise ServerNotFoundError()


    async def get_all(self) -> list[Server]:
        stmt = select(Server).filter(Server.status == 'active')
        result = await self.session.execute(stmt)
        return result.scalars().all()


class AuthSessionRepository(Repository):
    async def get_token(self, token: str, status='active'):
        stmt = select(AuthSession).filter(AuthSession.token == token, AuthSession.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().first()


class UserNotFoundError(Exception):
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.message = f"User with id {user_id} not found."
        super().__init__(self.message)


class ServerNotFoundError(Exception):
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.message = f"Server not found."
        super().__init__(self.message)

