from aiohttp import web
from sqlalchemy.orm import Session
from models import User

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    # with Session(autoflush=False, bind=engine) as db:
    #     bob = db.query(User).filter(User.id == 2).first()
    #     db.delete(bob)  # удаляем объект
    #     db.commit()  # сохраняем изменения
    return web.Response(text="Hello, world")
