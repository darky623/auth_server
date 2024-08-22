import asyncio
import uuid
from datetime import datetime

import config
from service import UserService
from database import UnitOfWork
from models import User, AuthSession

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(config.sqlite_database, echo=True)
AsyncSessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
uow = UnitOfWork(AsyncSessionFactory)

user_service = UserService(uow)

test_user_d = {
    'username': 'test',
    'email': 'test@mail.ru',
    'user_hash': 'fhfhfhfhfhfhfh',
    'create_date': datetime.now()
}

test_user = User(**test_user_d)


async def test():
    result = await user_service.get_by_id(2)
    print(result)
    auth_session = AuthSession(token=str(uuid.uuid1()), create_date=datetime.now())
    await user_service.add_auth_session(result, auth_session)


res = asyncio.run(test())


