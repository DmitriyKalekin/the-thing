from api.server import app

import asyncio
from aiohttp import ClientSession
import quart
from quart import Response, jsonify, request
import json
import ujson
from pprint import pprint

Response.default_mimetype = "application/json"

@app.route("/", methods=['POST', 'GET'])
async def index():
    r = await request.get_json()
    if request.method == 'POST':
        if 'callback_query' in r:
            print("CALLBACK detected ------------------------")
            pprint(r)
            await app.router.index_callback(r)
        elif 'message' in r:
            await app.router.index_message(r)
        # await app.telebot.sendMessage(435627225, "Незнакомый", disable_notification=True)

        # 
        # pprint(r)
        # if r["message"]["chat"].get("text", "") == "/group":
        #     # group chat
        #     if int(r["message"]["chat"]["id"]) < 0:
        #         channel_title = r["message"]["chat"]["title"]
        #         members = await app.client.get_participants(channel_title)
        #         for m in members:
        #             # UserStatusOffline
        #             # UserStatusOnline
        #             # UserStatusRecently
        #             print(m.id, m.bot, m.first_name, m.last_name, m.username, m.status.__class__.__name__)


        # nearest_sts = ["one", "two"]
        # r = await app.telebot.sendMessage(
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
    #         CommandsRouter.index_callback(r)
    #     elif 'message' in r:
    #         CommandsRouter.index_message(r)
    return jsonify({"status": 200, "index": "ok"})  #jsonify(json.dumps({"index": "ok"}), mimetype='application/json')

@app.route('/set_wh', methods=['POST', 'GET'])
async def tele_set_wh():
    res = await app.telebot.setWebhook(app.cfg.WH_URL)
    return jsonify(res)

@app.route(f'/get_wh', methods=['POST', 'GET'])
async def tele_get_wh_info():
    return jsonify(await app.telebot.getWebhookInfo())

@app.route(f'/del_wh', methods=['POST', 'GET'])
async def tele_del_wh():
    return jsonify(await app.telebot.deleteWebhook())

@app.route("/start_job")
async def start_job():
    player_id = 32768
    payload = {}
    # await app.model.create_job(player_id, payload)
    return jsonify({"status": "ok"})

@app.errorhandler(400)
async def bad_request(e):
    return jsonify({
        "status":   {
            "code": 400,
            "errorType": "bad_request",
            "errorDetails": "Bad request"
        }
    }), 400

@app.errorhandler(404)
async def page_not_found(e):
    return jsonify({
        "status":   {
            "code": 404,
            "errorType": "not_found",
            "errorDetails": "Not found this API section"
        }
    }), 404

@app.errorhandler(500)
async def internal_server_error(e):
    return jsonify({
        "status":   {
            "code": 500,
            "errorType": "not_supported",
            "errorDetails": "This query is not supported"
        }
    }), 500