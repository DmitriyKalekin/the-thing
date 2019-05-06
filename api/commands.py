import asyncio


class Invoker:

    def setup(self, app, r):
        self.app = app
        self.events_invoker = app["events_invoker"]
        self.telebot = app["telebot"]
        self.r = r        
        self.usr_fullname = f"{self.usr_first_name} {self.usr_last_name}"
        self.usr_notify = f"@{self.usr_username} {self.usr_first_name}" 
        self.method_to_call = self.blank_mock
        self.method_params = None

    def g(self):
        return self.app["games"].get_game(self.chat_id)
            
    async def blank_mock(self, *args, **kwargs):
        pass

    async def run_method(self, *args, **kwargs):
        return await self.method_to_call(*args, **kwargs)

    async def sendMessage(self, message, **kwargs):
        if "parse_mode" not in kwargs and "@" not in message:
            kwargs["parse_mode"] = "markdown"      
        return await self.telebot.sendMessage(self.chat_id, message, **kwargs)

    async def editMessageText(self, message_id, message, **kwargs):
        if "parse_mode" not in kwargs and "@" not in message:
            kwargs["parse_mode"] = "markdown"      
        return await self.telebot.editMessageText(self.chat_id, message_id, message, **kwargs)

    async def sendAnimation(self, animation, **kwargs):
        return await self.telebot.sendAnimation(self.chat_id, animation=animation, duration=30, width=80, height=18)


class MessageInvoker(Invoker):
    def __init__(self, app, r):
        self.chat_id = r["message"]["chat"]["id"]
        self.message = r["message"].get("text", "")
        self.usr = r["message"]["from"]
        self.usr_id = r["message"]["from"]["id"]
        self.usr_first_name = r["message"]["from"]["first_name"]
        self.usr_last_name = r["message"]["from"]["last_name"]
        self.usr_username = r["message"]["from"]["username"]
        self.setup(app, r)
        command_name = self.message.lower()
        if command_name[:1] == "/":
            if "@justiceleaguebot" in command_name:
                command_name = command_name.replace("@justiceleaguebot", "")
            self.method_to_call = getattr(self, 'cmd____' + command_name[1:], None)
            if not self.method_to_call:
                self.method_to_call = self._cmd_404
        return
    
    async def _cmd_404(self):
        return await self.sendMessage(f"Неизвестная команда *{self.message.lower()}*")

    async def cmd____start(self):
        return await self.sendMessage(f"Привет! Напиши [/play] если хочешь поиграть со мной)")

    async def cmd____play(self):
        # ----------- нельзя играть одному ---------------
        if self.chat_id > 0:
            return await self.sendMessage(f"{self.usr_first_name}, игру можно создать только в групповом чате не менее, чем на 4 человек.")
        # ----------- нельзя пересоздавать ---------------
        if len(self.g().players) > 0:
            return
            # # ----------- уже в игре ---------------
            # if self.usr_id in self.g()["players"]:
            #     return await self.sendMessage(f"{self.usr_notify}, Ты уже в игре. Подожди!")            
            # # ----------- еще не в игре ---------------
            # return await self.sendMessage(
            #     f"{self.usr_notify}, игра уже создаётся в этом чате. Присоединяйся!",
            #     reply_markup={"inline_keyboard": [[{"text": "✅ Присоединиться", "callback_data": "play:join"}]]}
            # )            
        # ----------- создаём игру на этот групповой чат ---------------
        await self.events_invoker.fire_event("join_game", {
            "chat_id": self.chat_id,
            "usr_id": self.usr_id,
            "usr_fullname": self.usr_fullname,
            "usr_alert": self.usr_notify
        })

        await self.sendMessage(
            f"*{self.usr_fullname}* желает начать новую игру.",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "✅ Присоединиться", "callback_data": "play:join"},
                    {"text": "🛑 Отказаться", "callback_data": "play:decline"}
                ]]
            } 
        )
        # await self.sendAnimation("https://eva-bot.ru/res/small_timer_00_30.gif")
        await self.task_countdown(timer=5)
        return None

    async def task_countdown(self, timer=59):
        r = await self.sendMessage(f"00:{timer}")
        print(r)
        await asyncio.sleep(1)
        for s in range(timer-1, -1, -1):
            if s < 10 or s % 10 == 0:
                tmr = str(s) if s >= 10 else f"0{str(s)}"
                await self.editMessageText(
                    r["result"]["message_id"],
                    f"00:{tmr}"
                )
            await asyncio.sleep(1)
        await self.events_invoker.fire_event("game_started", {"chat_id": self.chat_id})
        return await self.editMessageText(r["result"]["message_id"], "00:00 Поехали!")
           

class CallbackInvoker(Invoker):
    def __init__(self, app, r):
        self.chat_id = r["callback_query"]["message"]["chat"]["id"]
        self.callback_data = r["callback_query"]["data"]
        self.usr = r["callback_query"]["from"]
        self.usr_id = r["callback_query"]["from"]["id"]
        self.usr_first_name = r["callback_query"]["from"]["first_name"]
        self.usr_last_name = r["callback_query"]["from"]["last_name"]
        self.usr_username = r["callback_query"]["from"]["username"]
        self.setup(app, r)
               
        if self.callback_data:
            print(f"CALLBACK: {self.callback_data}")
            method, *self.method_params = self.callback_data.split(" ")
            self.method_to_call = getattr(self, 'callback____' + method.replace(":", "____"), None)
            if not self.method_to_call:
                self.method_to_call = self._callback_404
        return

    async def _callback_404(self):
        return await self.sendMessage(f"Неизвестный колбек `{self.callback_data}`")

    async def callback____play____join(self):
        await self.events_invoker.fire_event("join_game", {
            "chat_id": self.chat_id,
            "usr_id": self.usr_id,
            "usr_fullname": self.usr_fullname,
            "usr_alert": self.usr_notify
        })
        return await self.sendMessage(f"✅ *{self.usr_fullname}* в игре.")

    async def callback____play____decline(self):
        if self.usr_id in self.g()["players"]:
            del self.g()["players"][self.usr_id]
        return await self.sendMessage(f"_{self.usr_fullname} отказался._")

    async def callback____phase2____play_card(self):
        game = self.g()
        if not game:
            print("Нет игры")
            return
        print(game)

        if not game.board:
            print("Борда еще не создана в игре")
            return

        card_uuid = self.method_params
        card = self.g().board.get_player(self.usr_id).get_card_by_uuid(card_uuid)
        await self.events_invoker.fire_event("phase2:play_card", {
            "chat_id": self.chat_id,
            "usr_id": self.usr_id,
            "usr_fullname": self.usr_fullname,
            "usr_alert": self.usr_notify,
            "card_uuid": card_uuid
        })
        return await self.sendMessage(f"_{self.usr_fullname} играет карту *{card.name}*._")

    async def callback____phase2____drop_card(self):
        game = self.g()
        if not game:
            print("Нет игры")
            return
        print(game)

        if not game.board:
            print("Борда еще не создана в игре")
            return

        card_uuid = self.method_params
        card = game.board.get_player(self.usr_id).get_card_by_uuid(card_uuid)
        await self.events_invoker.fire_event("phase2:drop_card", {
            "chat_id": self.chat_id,
            "usr_id": self.usr_id,
            "usr_fullname": self.usr_fullname,
            "usr_alert": self.usr_notify,
            "card_uuid": card_uuid
        })
        return await self.sendMessage(f"_{self.usr_fullname} сбрасывает карту._")        


    






