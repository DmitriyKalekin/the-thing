from api.server import app
from quart import Response, request, jsonify
import json

@app.route("/")
async def index():
    return Response(json.dumps({"no": "a-a"}), mimetype='application/json')


@app.route("/start_job")
async def start_job():
    player_id = 32768
    payload = {}
    # await app.model.create_job(player_id, payload)
    return Response(json.dumps({"status": "ok"}), mimetype='application/json')

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