from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from aiohttp import web
from models import User
import config

routes = web.RouteTableDef()
engine = create_engine(config.sqlite_database, echo=True)


async def validate_form_data(form_data, required_fields):
    missing_fields = [field for field in required_fields if field not in form_data]
    if missing_fields:
        return False, f"{', '.join(missing_fields)} field(s) is missing"
    else:
        return True, None


@routes.post('/auth')
async def auth_handler(request):
    form_data = await request.post()
    is_valid, message = await validate_form_data(form_data, ['username', 'password'])
    if not is_valid:
        return web.HTTPBadRequest(text=message)

    username, password = str(form_data['username']), str(form_data['password'])
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.username == username, User.password == password).first()
        if not user:
            return web.HTTPBadRequest(text="User not found")

        return web.Response(text=f"User {user.username} has been successfully authorized!")


@routes.post('/register')
async def register_handler(request):
    form_data = await request.post()
    is_valid, message = await validate_form_data(form_data, ['email', 'username', 'password'])
    if not is_valid:
        return web.HTTPBadRequest(text=message)

    email, username, password = str(form_data['email']), str(form_data['username']), str(form_data['password'])
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
