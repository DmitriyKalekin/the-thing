from pprint import pprint
from aiohttp import web
# from api.server import reg

# async def handler(request):
#     data = {'some': 'data'}
#     return web.json_response(data)



async def index(request):
    r = await request.json()
    if request.method == 'POST':
        if 'callback_query' in r:
            print("CALLBACK detected ------------------------")
            pprint(r)
            await request.app["cmd"].index_callback(r)
        elif 'message' in r:
            await request.app["cmd"].index_message(r)
        # await request.app["telebot"].sendMessage(435627225, "Незнакомый", disable_notification=True)

        # 
        # pprint(r)
        # if r["message"]["chat"].get("text", "") == "/group":
        #     # group chat
        #     if int(r["message"]["chat"]["id"]) < 0:
        #         channel_title = r["message"]["chat"]["title"]
        #         members = await request.app.client.get_participants(channel_title)
        #         for m in members:
        #             # UserStatusOffline
        #             # UserStatusOnline
        #             # UserStatusRecently
        #             print(m.id, m.bot, m.first_name, m.last_name, m.username, m.status.__class__.__name__)


        # nearest_sts = ["one", "two"]
        # r = await request.app["telebot"].sendMessage(
        #     ,  
        #     "Тест клавиатуры в групповом чате", 
        #     parse_mode="markdown",
        #     # reply_markup={
        #     #     "keyboard": [[{"text": '/Опция {}'.format(n)}] for n in nearest_sts] }
        #    )
        # 435627225
        # 
    #     if 'callback_query' in r:
    #         print("CALLBACK detected ------------------------")
    #         Commandscmd.index_callback(r)
    #     elif 'message' in r:
    #         Commandscmd.index_message(r)
    return web.json_response({"status": 200, "index": "ok"})  #return web.json_response(json.dumps({"index": "ok"}), mimetype='application/json')

async def set_wh(request):
    res = await request.app["telebot"].setWebhook(request.app["cfg"].WH_URL)
    return web.json_response(res)

async def get_wh(request):
    return web.json_response(await request.app["telebot"].getWebhookInfo())

async def del_wh(request):
    return web.json_response(await request.app["telebot"].deleteWebhook())

async def start_job(request):
    player_id = 32768
    payload = {}
    # await request.app.model.create_job(player_id, payload)
    return web.json_response({"status": "ok"})


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