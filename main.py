from aiohttp_middlewares import cors_middleware
from routes import routes, engine, create_test_server
from models import Base
from aiohttp import web
import config
import ssl
import asyncio


async def setup():
    print('Запуск...')
    # await create_test_server()
    app = web.Application()
    cors = cors_middleware(
        allow_all=True,
        allow_credentials=True,
        allow_headers=("Content-Type", "Authorization"),
        allow_methods=("GET", "POST", "OPTIONS"))
    app.middlewares.append(cors)
    app.add_routes(routes)
    app.on_cleanup.append(shutdown)

    return app


async def shutdown(app):
    print('Выключение...')


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    # asyncio.run(init_db())
    context = None
    if config.webhook_port == 443:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config.webhook_ssl_cert, config.webhook_ssl_priv)

    web.run_app(setup(), host='0.0.0.0', port=config.webhook_port, ssl_context=context)
