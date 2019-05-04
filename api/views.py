from aiohttp import web
from api.commands import MessageInvoker, CallbackInvoker


async def post_index(request):
    r = await request.json()
    print(r)
    if 'callback_query' in r:
        await CallbackInvoker(request.app, r).run_method()
    elif 'message' in r and r["message"].get("text", "")[:1] == "/":
        await MessageInvoker(request.app, r).run_method()
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