from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from aiohttp import web
from models import User
import config
import json

routes = web.RouteTableDef()
engine = create_engine(config.sqlite_database, echo=True)


async def validate_form_data(byte_str, required_fields):
    decoded_str = byte_str.decode('utf-8')
    try:
        data = json.loads(decoded_str)
    except json.decoder.JSONDecodeError as e:
        return None, 'Ошибка декодирования'

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return None, f"{', '.join(missing_fields)} field(s) is missing"
    else:
        return data, None


@routes.post('/auth')
async def auth_handler(request):
    byte_str = await request.read()
    data, message = await validate_form_data(byte_str, ['username', 'password'])
    if not data:
        return web.HTTPBadRequest(text=message)

    username, password = str(data['username']), str(data['password'])
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.username == username, User.password == password).first()
        if not user:
            return web.HTTPBadRequest(text="User not found")

        return web.Response(text=f"User {user.username} has been successfully authorized!")


@routes.post('/register')
async def register_handler(request):
    byte_str = await request.read()
    data, message = await validate_form_data(byte_str, ['email', 'username', 'password'])
    if not data:
        return web.HTTPBadRequest(text=message)

    email, username, password = str(data['email']), str(data['username']), str(data['password'])
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return web.HTTPBadRequest(text="This username is already registered")

        user = db.query(User).filter(User.email == email).first()
        if user:
            return web.HTTPBadRequest(text="This email is already registered")

        user = User(email=email, username=username, password=password)
        db.add(user)
        db.commit()

        return web.Response(text=f"User {user.username} has been successfully registered!")
