import asyncio
# from api.jobs import jobs_loop
import ssl
from aiohttp import web, ClientSession
from app.routes import setup_routes
from app.telebot import Telebot
from app.jobs import jobs_loop
from app.events import EventsQueue
from app.commands import CommandsObserver
# from app.commands import EventsInvoker
from config import get_config
import ujson
import random

# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# from game.misc import get_group_memgers
# from api.registry import Registry

# async def main222(loop):
#     app.CFG = CFG
#     app.loop = loop
#     asyncio.ensure_future(jobs_loop())

# Configure logging
# logging.basicConfig(level=logging.INFO)

        
async def close_session(app):
    if app["session"] is not None:
        await app["session"].close()


async def shutdown(app):
    await app["session"].close()  
    await app.shutdown()

async def init(loop, events_queue):
    cfg = get_config()
    app = web.Application(loop=loop)
    app["loop"] = loop
    app["jobs"] = []
    app["cfg"] = cfg
    app["session"] = ClientSession(loop=loop, json_serialize=ujson.dumps)  # TODO: можно полностью поместить только в телебота
    app["telebot"] = Telebot(cfg.URL, app["session"])
    app["games"] = dict()
    app["events"] = events_queue
    app["events"].register_observer(CommandsObserver(app))
    # await app["events"].set_application(app)
    setup_routes(app)
    app.on_cleanup.append(shutdown)
    return app


def main():
    random.seed(6)
    # random.seed(1)
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain('/etc/ssl/eva-bot.ru/flask.pem', '/etc/ssl/eva-bot.ru/certificate.key')
    loop = asyncio.get_event_loop()
    events_queue = EventsQueue()
    
    try:
        asyncio.ensure_future(jobs_loop())
        asyncio.ensure_future(events_queue.listen())
        web.run_app(init(loop, events_queue), host="0.0.0.0", port=8443, ssl_context=ssl_ctx, reuse_port=True)
    except (SystemExit, KeyboardInterrupt):
        print('Stopping service...')
    finally:
        loop.close()
    print('Service stopped.')


if __name__ == "__main__":
    main()

