from api.server import app
import asyncio
from aiohttp import ClientSession
import quart
from quart import Response, jsonify, request
import json
import ujson

Response.default_mimetype = "application/json"

@app.route("/", methods=['POST', 'GET'])
async def index():
    if request.method == 'POST':
        r = await request.get_json()
        print(r)
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
def bad_request(e):
    return jsonify({
        "status":   {
            "code": 400,
            "errorType": "bad_request",
            "errorDetails": "Bad request"
        }
    }), 400

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "status":   {
            "code": 404,
            "errorType": "not_found",
            "errorDetails": "Not found this API section"
        }
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "status":   {
            "code": 500,
            "errorType": "not_supported",
            "errorDetails": "This query is not supported"
        }
    }), 500