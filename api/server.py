from quart import Quart
from api.telebot import Telebot
from api.commands import CommandsRouter
from config import get_config
from telethon import TelegramClient, sync
from telethon import utils
# from flask import Flask


app = Quart(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.jobs = []
app.cfg = get_config()
app.telebot = Telebot(app.cfg.URL)
app.games = dict()
app.router = CommandsRouter(app)

# app.client = TelegramClient('session_name', cfg.API_ID, cfg.API_HASH).start()
# app.client.connect()
# if not app.client.is_user_authorized():
#     app.client.send_code_request(phone_number)
#     me = app.client.sign_in(cfg.API_PHONE_NUMBER, input('Enter code: '))
# app.client.send_message('@herr_horror', 'Server started.\nClient loaded.') 
# members = app.client.get_participants('TheThingDevTest')
# for m in members:
#     # UserStatusOffline
#     # UserStatusOnline
#     # UserStatusRecently
#     print(m.id, m.bot, m.first_name, m.last_name, m.username, m.status.__class__.__name__)




