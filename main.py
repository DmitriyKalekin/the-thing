# import asyncio
# import aiomysql
from api.server import app
from api.views import *
from api.jobs import jobs_loop
from config import CFG

# async def main(loop):
#     app.CFG = CFG
#     app.loop = loop
#     asyncio.ensure_future(jobs_loop())


if __name__ == "__main__":
    try:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(main(loop))
        app.run()
    except KeyboardInterrupt:
        print("Exiting")
