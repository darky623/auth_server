from models import User, AuthSession, Server
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from hashlib import sha256
from aiohttp import web
import config
import json
import hmac
import uuid

routes = web.RouteTableDef()
engine = create_engine(config.sqlite_database, echo=True)


# Create test server
def create_test_server():
    with Session(autoflush=False, bind=engine) as db:
        test_server = Server(address='31.129.54.121', name='#1 Alpha', create_date=datetime.now())
        db.add(test_server)
        db.commit()


def validate_form_data(byte_str, required_fields):
    decoded_str = byte_str.decode('utf-8')
    try:
        data = json.loads(decoded_str)
    except json.decoder.JSONDecodeError as e:
        return None, "It is not JSON data"

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return None, f"{', '.join(missing_fields)} field(s) is missing"
    else:
        return data, None


def get_user_hash(data, secret_key=config.secret_key):
    data_check_string = "\n".join([f"{key}={value}" for key, value in sorted(data.items()) if value is not None])
    user_hash = hmac.new(sha256(secret_key.encode()).digest(), data_check_string.encode(), sha256).hexdigest()

    return user_hash


def check_auth_token(token: str):
    user_data, token_data = None, None
    with Session(autoflush=False, bind=engine) as db:
        token_data = db.query(AuthSession).filter(AuthSession.token == token, AuthSession.status == 'active').first()
        if token_data:
            if (datetime.now()-token_data.create_date) <= timedelta(seconds=config.token_lifetime):
                user_data = token_data.user
            else:
                token_data.status = 'expired'
                db.commit()

    return user_data, token_data


@routes.post('/auth')
async def auth_handler(request):
    byte_str = await request.read()
    response = {"message": None, "token": None}
    data, message = validate_form_data(byte_str, ['username', 'password'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    user_hash = get_user_hash({"username": data['username'], "password": data['password']})
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.user_hash == user_hash).first()
        if not user:
            response["message"] = "Username or password is incorrect"
            return web.json_response(response)

        response["message"] = f"User {user.username} has been successfully authorized!"
        auth_session = AuthSession(token=str(uuid.uuid1()), create_date=datetime.now())
        user.auth_sessions.append(auth_session)
        db.commit()
        response["token"] = auth_session.token

        return web.json_response(response)


@routes.post('/register')
async def register_handler(request):
    byte_str = await request.read()
    response = {"message": None, "token": None}
    data, message = validate_form_data(byte_str, ['email', 'username', 'password'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    with Session(autoflush=False, bind=engine) as db:
        if db.query(User).filter(User.username == str(data['username'])).first():
            response["message"] = "This username is already registered"
            return web.json_response(response)

        if db.query(User).filter(User.email == str(data['email'])).first():
            response["message"] = "This email is already registered"
            return web.json_response(response)

        user_hash = get_user_hash({'username': data['username'], 'password': data['password']})
        auth_session = AuthSession(token=str(uuid.uuid1()), create_date=datetime.now())
        user = User(email=data['email'], username=data['username'], user_hash=user_hash, create_date=datetime.now())
        user.auth_sessions.append(auth_session)
        response["message"] = f"User {user.username} has been successfully registered!"
        db.add(user)
        db.commit()
        response["token"] = auth_session.token

        return web.json_response(response)


@routes.get('/servers')
async def servers_handler(request):
    byte_str = await request.read()
    response = {"message": "Please select a server", "servers": []}
    data, message = validate_form_data(byte_str, ['token'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    user, token_data = check_auth_token(data['token'])
    if not user:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    with Session(autoflush=False, bind=engine) as db:
        for s in db.query(Server).filter(Server.status == 'active').all():
            server = {"id": s.id, "name": s.name, "locale": s.locale, "address": s.address}
            response["servers"].append(server)

    return web.json_response(response)


@routes.get('/token')
async def servers_handler(request):
    byte_str = await request.read()
    response = {"message": "This token belongs to the user", "user": None, "token": None}
    data, message = validate_form_data(byte_str, ['token'])
    if not data:
        response["message"] = message
        return web.json_response(response)

    user, token_data = check_auth_token(data['token'])
    if not user:
        response["message"] = "Token is invalid!"
        return web.json_response(response)

    else:
        response["user"] = user.serialize()
        response["token"] = token_data.serialize()
        return web.json_response(response)
