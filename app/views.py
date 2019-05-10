from aiohttp import web
from app.telebot import Callback, Message
# from api.commands import MessageInvoker, CallbackInvoker
# from api.events import EventMessage, EventCallback

async def post_index(request):
    r = await request.json()
    # print(r)
    if 'callback_query' in r:
        callback = Callback(r)
        assert callback.id is not None
        assert callback.sender is not None
        assert callback.chat_id is not None
        assert callback.data is not None
        await request.app["events"].notify_callbacks(callback)
    elif 'message' in r:
        message = Message(r)
        assert message.id is not None
        assert message.sender is not None
        assert message.chat_id is not None
        assert message.text != ""        
        if message.text[:1] == "/":
            await request.app["events"].notify_observers(message)
    return web.json_response({"status": 200, "index": "ok"})


async def set_wh(request):
    res = await request.app["telebot"].setWebhook(request.app["cfg"].WH_URL)
    return web.json_response(res)


async def get_wh(request):
    return web.json_response(await request.app["telebot"].getWebhookInfo())


async def del_wh(request):
    return web.json_response(await request.app["telebot"].deleteWebhook())


async def start_job(request):
    # player_id = 32768
    # payload = {}
    # await request.app.model.create_job(player_id, payload)
    return web.json_response({"status": 200})


# async def bad_request(e):
#     return web.json_response({
#         "status":   {
#             "code": 400,
#             "errorType": "bad_request",
#             "errorDetails": "Bad request"
#         }
#     }), 400


# async def page_not_found(e):
#     return web.json_response({
#         "status":   {
#             "code": 404,
#             "errorType": "not_found",
#             "errorDetails": "Not found this API section"
#         }
#     }), 404


# async def internal_server_error(e):
#     return web.json_response({
#         "status":   {
#             "code": 500,
#             "errorType": "not_supported",
#             "errorDetails": "This query is not supported"
#         }
#     }), 500