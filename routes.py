from models import AuthSession, Server
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database import UnitOfWork
from service import UserService, ServerService, CredentialsException
from utils import *

routes = web.RouteTableDef()
engine = create_async_engine(config.sqlite_database, echo=True)
AsyncSessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
uow = UnitOfWork(AsyncSessionFactory)
user_service = UserService(uow)
server_service = ServerService(uow)


# Create test server
async def create_test_server():
    servers = []
    async with uow.start() as uow_session:
        servers.append(Server(address='127.0.0.1', name=f'#0 Localhost', create_date=datetime.now(), status='test'))
        for i in range(20):
            servers.append(Server(address='31.129.54.121', name=f'#{i+1} Alpha', create_date=datetime.now()))
            uow_session._session.add_all(servers)
            await uow_session._session.flush()


def check_auth_token(token: str):
    user_data, token_data = None, None
    with Session(autoflush=False, bind=engine) as db:
        auth_data = db.query(AuthSession).filter(AuthSession.token == token, AuthSession.status == 'active').first()
        if auth_data:
            if (datetime.now()-auth_data.create_date) <= timedelta(seconds=config.token_lifetime):
                user_data = auth_data.user
            else:
                auth_data.status = 'expired'
                db.commit()

    return user_data, auth_data


@routes.post('/auth')
async def auth_handler(request):
    byte_str = await request.read()
    response = {"message": None, "token": None}
    data, message = validate_form_data(byte_str, ['username', 'password'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    try:
        token = await user_service.verify_user_and_generate_token(data)
        response["token"] = token
        response["message"] = f"User {data['username']} has been successfully authorized!"
    except CredentialsException as e:
        response["message"] = "Username or password is incorrect"

    return web.json_response(response)


@routes.post('/register')
async def register_handler(request):
    byte_str = await request.read()
    response = {"message": None, "token": None}
    data, message = validate_form_data(byte_str, ['email', 'username', 'password'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    try:
        if await user_service.get_user(email=data['email']):
            response["message"] = "This username is already registered"
            return web.json_response(response)
    except:
        ... # Тут по хорошему надо бросать ошибку 400

    try:
        if await user_service.get_user(email=data['username']):
            response["message"] = "This email is already registered"
            return web.json_response(response)
    except:
        ... # Тут по хорошему надо бросать ошибку 400

    token = await user_service.add(data)

    response["message"] = f"User {data['username']} has been successfully registered!"
    response["token"] = token

    return web.json_response(response)


@routes.get('/servers')
async def servers_handler(request):
    byte_str = await request.read()
    response = {"message": "Please select a server", "servers": []}
    data, message = validate_form_data(byte_str, ['token'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    if not await user_service.check_token(data['token']):
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    for server in await server_service.get_all():
        response["servers"].append(server.serialize())

    return web.json_response(response)


@routes.get('/token')
async def token_handler(request):
    byte_str = await request.read()
    response = {"message": "This token belongs to the user", "user": None, "auth": None}
    data, message = validate_form_data(byte_str, ['token'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    with Session(autoflush=False, bind=engine) as db:
        server = db.query(Server).filter(Server.address == str(request.remote)).first()
        if not server:
            response["message"] = "The remote host is not in the allowed list."
            return web.json_response(response)

    user, auth_data = check_auth_token(data['token'])
    if not user:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    else:
        response["user"] = user.serialize()
        response["auth"] = auth_data.serialize()
        return web.json_response(response)
