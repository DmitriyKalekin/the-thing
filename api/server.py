from quart import Quart
from api.telebot import Telebot
from config import get_config
# from flask import Flask


app = Quart(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.jobs = []
app.cfg = get_config()
app.telebot = Telebot(app.cfg.URL)





