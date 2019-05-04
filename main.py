import asyncio
# import aiomysql

# from api.jobs import jobs_loop
# from config import get_config
import ssl
from aiohttp import web, ClientSession
from api.routes import setup_routes
from api.telebot import Telebot
from api.jobs import jobs_loop
from config import get_config
import ujson

# from api.registry import Registry

# from telethon import TelegramClient, sync
# from telethon import utils

# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# async def main222(loop):
#     app.CFG = CFG
#     app.loop = loop
#     asyncio.ensure_future(jobs_loop())


async def close_session(app):
    if app["session"] is not None:
        await app["session"].close()


# async def l():
#     await asyncio.sleep(10)


async def shutdown(app):
    # server.close()
    # await server.wait_closed()
    await app["session"].close()  # database connection close
    await app.shutdown()
    # await handler.finish_connections(10.0)
    # await app.cleanup()    


async def init(loop):
    cfg = get_config()
    app = web.Application(loop=loop)
    app["loop"] = loop
    app["jobs"] = []
    app["cfg"] = cfg
    app["session"] = ClientSession(loop=loop, json_serialize=ujson.dumps)
    app["telebot"] = Telebot(cfg.URL, app["session"])
    app["games"] = dict()
    setup_routes(app)
    app.on_cleanup.append(shutdown)
    return app


def main():
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain('/etc/ssl/eva-bot.ru/flask.pem', '/etc/ssl/eva-bot.ru/certificate.key')
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(jobs_loop())
        web.run_app(init(loop), host="0.0.0.0", port=8443, ssl_context=ssl_ctx, reuse_port=True)
    except (SystemExit, KeyboardInterrupt):
        print('Stopping service...')
    finally:
        loop.close()
    print('Service stopped.')


if __name__ == "__main__":
    main()

