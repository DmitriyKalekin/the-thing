import asyncio
from app.game import Game
from app.game_view import GameView
# 
# from pprint import pprint
# import traceback
from app.telebot import Message


class CommandsObserver:
    def __init__(self, app):
        self.app = app
        self.telebot = app["telebot"]

    async def update(self, msg):
        if type(msg) != Message:
            return
        command_name = msg.text.lower().replace("@justiceleaguebot", "").strip()
        if command_name[:1] == "/":
            method_to_call = getattr(self, 'cmd____' + command_name[1:], None)
            if not method_to_call:
                method_to_call = self._cmd_404
        await method_to_call(msg)

    async def _cmd_404(self, msg):
        return await self.telebot.sendMessage(msg.chat_id, f"Неизвестная команда *{msg.text.lower()}*")

    async def cmd____start(self, msg):
        return await self.telebot.sendMessage(msg.chat_id, f"Привет! Я тут главный по играм. Напиши [/play] если хочешь поиграть со мной)")

    async def cmd____play(self, msg):
        if msg.chat_id > 0:  # нельзя играть одному
            await self.telebot.sendMessage(msg.chat_id, f"{msg.sender.first_name}, игру можно создать только в групповом чате не менее, чем на 4 человек.")
            return 
        
        if self.app["games"].get(msg.chat_id, None) is not None:  # нельзя пересоздать игру
            return

        assert msg.chat_id < 0
        game = Game()
        game.init(msg.chat_id, self.app)
        game.set_view(GameView())
        game.add_player(msg.sender.id)
        self.app["games"][msg.chat_id] = game

        await self.telebot.sendMessage(msg.chat_id,
            f"*{msg.sender.first_name} {msg.sender.last_name}* желает начать новую игру.",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "✔️ Присоединиться", "callback_data": "/play:join"},
                    {"text": "👎 Отказаться", "callback_data": "/play:decline"}
                ]]
            } 
        )
        # await self.sendAnimation("https://eva-bot.ru/res/small_timer_00_30.gif")
        self.app.loop.create_task(self.set_timeout_function(msg.chat_id, game.start, timer=1))
        return

    async def set_timeout_function(self, chat_id, call_later, timer=10):
        r = await self.telebot.sendMessage(chat_id, f"00:{timer}")
        msg_id = r["result"]["message_id"]
        await asyncio.sleep(1)
        for s in range(timer-1, -1, -1):
            await asyncio.sleep(0)
            if s < 10 or s % 10 == 0:
                tmr = str(s) if s >= 10 else f"0{str(s)}"
                await self.telebot.editMessageText(chat_id, msg_id, f"00:{tmr}")
            await asyncio.sleep(1)
        # await self.events_invoker.fire_event("game_started", {"chat_id": self.chat_id})
        await self.telebot.editMessageText(chat_id, msg_id, "00:00!")
        await call_later()

        # method_name = e.get("name", "")
        # method_to_call = getattr(self, 'event____' + method_name, None) 
        # if not method_to_call:
        #     print(f"ERROR: неизвестное событие: {method_name}")
        #     return
        # del e["name"]
        # print(f"Получено событие: {method_name}")
        # return await method_to_call(**e)
# class EventsInvoker:
#     async def invoke():

#     def g(self, chat_id) -> Game:
#         return self.app["games"].get_game(chat_id)

#     # async def fire_event(self, name, params: dict):
#     #     self.events.append({"name": name, **params})
#     #     return



#     async def event____create_game(self, chat_id=0, user_id=None):
#         assert chat_id < 0
#         assert user_id > 0
#         print(f"Создана или существует игра в {chat_id}")
#         self.g(chat_id).add_player(user_id)
#         return 
    
#     async def event____join_game(self, chat_id=0, user_id=None, user_fullname=None, user_alert=None):
#         assert chat_id < 0
#         assert user_id > 0
#         print(f"Игрок присоединился в {chat_id}")
#         game = self.g(chat_id)
#         # войти можно только в неначатую игру
#         if game.status == Game.STATUS_PENDING:
#             self.g(chat_id).add_player({"user_id": user_id, "chat_id": chat_id, "user_fullname": user_fullname, "user_alert": user_alert})
#         return

#     async def event____game_started(self, chat_id=0):
#         assert chat_id < 0
#         if not self.g(chat_id).can_start() and chat_id != -272083086:
#             self.g(chat_id).status = Game.STATUS_CANCELED
#             await self.self.print(chat_id, "Не набрали необходимое количество человек (4). Игра отменена.")
#             return
        
#         self.g(chat_id).status = Game.STATUS_LAUNCHED
#         self.g(chat_id).create_board()
#         await self.g(chat_id).run()
#         await self.print(chat_id, "Игра началась")




         

       

#     async def listen(self):
#         """
#         """
#         while True:
#             for e in self.events:
#                 await self.invoke(e)
#             await asyncio.sleep(1)
#         return


# class Invoker:

#     def setup(self, app, r):
#         self.app = app
#         self.events_invoker = app["events_invoker"]
#         self.telebot = app["telebot"]
#         self.r = r        
#         self.user_fullname = f"{self.user_first_name} {self.user_last_name}"
#         self.user_notify = f"@{self.user_username} {self.user_first_name}" 
#         self.method_to_call = self.blank_mock
#         self.method_params = None

#     def g(self):
#         return self.app["games"].get_game(self.chat_id)
            
#     async def blank_mock(self, *args, **kwargs):
#         pass

#     async def run_method(self, *args, **kwargs):
#         return await self.method_to_call(*args, **kwargs)

#     async def sendMessage(self, message, **kwargs):
#         if "parse_mode" not in kwargs and "@" not in message:
#             kwargs["parse_mode"] = "markdown"      
#         return await self.telebot.sendMessage(self.chat_id, message, **kwargs)

#     async def editMessageText(self, message_id, message, **kwargs):
#         if "parse_mode" not in kwargs and "@" not in message:
#             kwargs["parse_mode"] = "markdown"      
#         return await self.telebot.editMessageText(self.chat_id, message_id, message, **kwargs)

#     async def sendAnimation(self, animation, **kwargs):
#         return await self.telebot.sendAnimation(self.chat_id, animation=animation, duration=30, width=80, height=18)


# class MessageInvoker(Invoker):
#     def __init__(self, app, r):
#         self.chat_id = r["message"]["chat"]["id"]
#         self.message = r["message"].get("text", "")
#         self.user = r["message"]["from"]
#         self.user_id = r["message"]["from"]["id"]
#         self.user_first_name = r["message"]["from"]["first_name"]
#         self.user_last_name = r["message"]["from"]["last_name"]
#         self.user_username = r["message"]["from"]["username"]
#         self.setup(app, r)
#         command_name = self.message.lower()
#         if command_name[:1] == "/":
#             if "@justiceleaguebot" in command_name:
#                 command_name = command_name.replace("@justiceleaguebot", "")
#             self.method_to_call = getattr(self, 'cmd____' + command_name[1:], None)
#             if not self.method_to_call:
#                 self.method_to_call = self._cmd_404
#         return
    

           

# class CallbackInvoker(Invoker):
#     def __init__(self, app, r):
#         self.chat_id = r["callback_query"]["message"]["chat"]["id"]
#         self.callback_data = r["callback_query"]["data"]
#         self.user = r["callback_query"]["from"]
#         self.user_id = r["callback_query"]["from"]["id"]
#         self.user_first_name = r["callback_query"]["from"]["first_name"]
#         self.user_last_name = r["callback_query"]["from"]["last_name"]
#         self.user_username = r["callback_query"]["from"]["username"]
#         self.setup(app, r)
               
#         if self.callback_data:
#             print(f"CALLBACK: {self.callback_data}")
#             method, *self.method_params = self.callback_data.split(" ")
#             self.method_to_call = getattr(self, 'callback____' + method.replace(":", "____"), None)
#             if not self.method_to_call:
#                 self.method_to_call = self._callback_404
#         return

#     async def _callback_404(self):
#         return await self.sendMessage(f"Неизвестный колбек `{self.callback_data}`")

#     async def callback____play____join(self):
#         await self.events_invoker.fire_event("join_game", {
#             "chat_id": self.chat_id,
#             "user_id": self.user_id,
#             "user_fullname": self.user_fullname,
#             "user_alert": self.user_notify
#         })
#         return await self.sendMessage(f"✅ *{self.user_fullname}* в игре.")

#     async def callback____play____decline(self):
#         if self.user_id in self.g()["players"]:
#             del self.g()["players"][self.user_id]
#         return await self.sendMessage(f"_{self.user_fullname} отказался._")

#     async def callback____phase2____play_card(self):
#         game = self.g()
#         if not game:
#             print("Нет игры")
#             return
#         print(game)

#         if not game.board:
#             print("Борда еще не создана в игре")
#             return

#         card_uuid = self.method_params
#         card = self.g().board.get_player(self.user_id).get_card_by_uuid(card_uuid)
#         await self.events_invoker.fire_event("phase2:play_card", {
#             "chat_id": self.chat_id,
#             "user_id": self.user_id,
#             "user_fullname": self.user_fullname,
#             "user_alert": self.user_notify,
#             "card_uuid": card_uuid
#         })
#         return await self.sendMessage(f"_{self.user_fullname} играет карту *{card.name}*._")

#     async def callback____phase2____drop_card(self):
#         game = self.g()
#         if not game:
#             print("Нет игры")
#             return
#         print(game)

#         if not game.board:
#             print("Борда еще не создана в игре")
#             return

#         card_uuid = self.method_params
#         card = game.board.get_player(self.user_id).get_card_by_uuid(card_uuid)
#         await self.events_invoker.fire_event("phase2:drop_card", {
#             "chat_id": self.chat_id,
#             "user_id": self.user_id,
#             "user_fullname": self.user_fullname,
#             "user_alert": self.user_notify,
#             "card_uuid": card_uuid
#         })
#         return await self.sendMessage(f"_{self.user_fullname} сбрасывает карту._")        


    






