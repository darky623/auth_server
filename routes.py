from models import AuthSession, Server
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database import UnitOfWork
from service import UserService, ServerService, CredentialsException
from packaging.version import Version
from utils import *
import config
import os

routes = web.RouteTableDef()
engine = create_async_engine(config.sqlite_database, echo=True)
AsyncSessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
uow = UnitOfWork(AsyncSessionFactory)
user_service = UserService(uow)
server_service = ServerService(uow)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FILE_PATH = os.path.join(BASE_DIR, 'frontend.html')
FRONTEND_REG_FILE_PATH = os.path.join(BASE_DIR, 'frontend-reg.html')
min_build_version = Version(config.min_build_version)

# Create test server
async def create_test_server():
    servers = [Server(address='127.0.0.1', name=f'#0 Localhost', create_date=datetime.now(), status='test')]
    for i in range(20):
        servers.append(Server(address='lotw-api.clava.space', name=f'#{i+1} Alpha', create_date=datetime.now()))
        await server_service.add_many(servers)

@routes.get('/auth')
async def auth_frontend_handler(request):
    try:
        with open(FRONTEND_FILE_PATH, 'r') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(text="HTML файл не найден", status=404)


@routes.get('/reg')
async def reg_frontend_handler(request):
    try:
        with open(FRONTEND_REG_FILE_PATH, 'r') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(text="HTML файл не найден", status=404)



@routes.post('/auth')
async def auth_handler(request):
    byte_str = await request.read()
    response = {"message": None, "token": None}
    current_build_version = Version("0")
    data, message = validate_form_data(byte_str, ['username', 'password', 'build_version'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    try:
        current_build_version = Version(data['build_version'])
    except Exception as e:
        response["message"] = "Parameter build_version is not valid"
        return web.json_response(response)

    if current_build_version < min_build_version:
        response["message"] = "The build version is not up to date"
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

    if not config.allow_user_registration:
        response["message"] = "Registration of new users is temporarily unavailable."
        return web.json_response(response)

    try:
        if is_valid_email(data['email']):
            if await user_service.get_user(email=data['email']):
                response["message"] = "This email is already registered"
                return web.json_response(response)
        else:
            response["message"] = "This email is invalid"
            return web.json_response(response)
    except:
        ... # Тут по хорошему надо бросать ошибку 400

    try:
        if await user_service.get_user(email=data['username']):
            response["message"] = "This username is already registered"
            return web.json_response(response)
    except:
        ... # Тут по хорошему надо бросать ошибку 400

    token = await user_service.add(data)

    response["message"] = f"User {data['username']} has been successfully registered!"
    response["token"] = token

    return web.json_response(response)


@routes.get('/servers')
async def servers_handler(request):
    response = {"message": "Please select a server", "servers": []}
    try:
        for server in await server_service.get_all():
            response["servers"].append(server.serialize())
    except:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    return web.json_response(response)


@routes.get('/token')
async def token_handler(request):
    response = {"message": "This token belongs to the user", "user": None, "auth": None}
    try:
        token = get_token(request)
    except:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    server = await server_service.get_by_address(request.remote)
    if not server:
        response["message"] = "The remote host is not in the allowed list."
        return web.json_response(response)

    user, auth_data = await user_service.check_token(token)
    if not user:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    else:
        response["user"] = user.serialize()
        response["auth"] = auth_data.serialize()
        return web.json_response(response)
