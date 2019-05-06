import asyncio
# from api.jobs import jobs_loop
import ssl
from aiohttp import web, ClientSession
from api.routes import setup_routes
from api.telebot import Telebot
from api.jobs import jobs_loop
from api.events import EventsInvoker
from game.board import Games
from config import get_config
import ujson
import random
# from game.misc import get_group_memgers
# from api.registry import Registry
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# async def main222(loop):
#     app.CFG = CFG
#     app.loop = loop
#     asyncio.ensure_future(jobs_loop())



        
async def close_session(app):
    if app["session"] is not None:
        await app["session"].close()


async def shutdown(app):
    # server.close()
    # await server.wait_closed()
    await app["session"].close()  # database connection close
    await app.shutdown()
    # await handler.finish_connections(10.0)
    # await app.cleanup()    


async def init(loop, events_invoker):
    cfg = get_config()
    app = web.Application(loop=loop)
    app["loop"] = loop
    app["jobs"] = []
    app["cfg"] = cfg
    app["session"] = ClientSession(loop=loop, json_serialize=ujson.dumps)  # TODO: можно полностью поместить только в телебота
    app["telebot"] = Telebot(cfg.URL, app["session"])
    app["games"] = Games(app)
    app["events_invoker"] = events_invoker
    app["events_invoker"].set_application(app)
    setup_routes(app)
    app.on_cleanup.append(shutdown)
    return app


def main():
    random.seed(6)
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain('/etc/ssl/eva-bot.ru/flask.pem', '/etc/ssl/eva-bot.ru/certificate.key')
    loop = asyncio.get_event_loop()
    events_invoker = EventsInvoker()
    try:
        asyncio.ensure_future(jobs_loop())
        asyncio.ensure_future(events_invoker.listen())
        web.run_app(init(loop, events_invoker), host="0.0.0.0", port=8443, ssl_context=ssl_ctx, reuse_port=True)
    except (SystemExit, KeyboardInterrupt):
        print('Stopping service...')
    finally:
        loop.close()
    print('Service stopped.')


if __name__ == "__main__":
    main()

