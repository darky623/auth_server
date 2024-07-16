from aiohttp_middlewares import cors_middleware
from sqlalchemy import create_engine
from routes import routes
from aiohttp import web
from models import Base
import config
import ssl


async def setup():
    print('Запуск...')
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


if __name__ == '__main__':
    engine = create_engine(config.sqlite_database, echo=True)
    Base.metadata.create_all(bind=engine)
    context = None
    if config.webhook_port == 443:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config.webhook_ssl_cert, config.webhook_ssl_priv)

    web.run_app(setup(), host='0.0.0.0', port=config.webhook_port, ssl_context=context)
