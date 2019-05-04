# import asyncio
# import aiomysql
from api.server import app
from api.views import *
from api.jobs import jobs_loop
from config import get_config



# async def main(loop):
#     app.CFG = CFG
#     app.loop = loop
#     asyncio.ensure_future(jobs_loop())


if __name__ == "__main__":
    try:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(main(loop))
        app.run(host="0.0.0.0", port=8443, certfile="/etc/ssl/eva-bot.ru/flask.pem", keyfile="/etc/ssl/eva-bot.ru/certificate.key", debug=True, use_reloader=True)
        # app.run(debug=True)
    except KeyboardInterrupt:
        await app.session.close()
        print("Exiting")

