from contextlib import asynccontextmanager
from repository import UserRepository, ServerRepository, AuthSessionRepository


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None
        self._repositories = {}

    @asynccontextmanager
    async def start(self):
        self._session = self.session_factory()
        try:
            yield self
            await self._session.commit()
        except:
            await self._session.rollback()
            raise
        finally:
            await self._session.close()

    @property
    def users(self) -> UserRepository:
        return UserRepository(self._session)

    @property
    def servers(self) -> ServerRepository:
        return ServerRepository(self._session)

    @property
    def auth_sessions(self) -> AuthSessionRepository:
        return AuthSessionRepository(self._session)
