class Invoker:
    async def blank_mock(self, *args, **kwargs):
        pass

    async def run_method(self, *args, **kwargs):
        return await self.method_to_call(*args, **kwargs)

    async def sendMessage(self, message, **kwargs):
        if "parse_mode" not in kwargs and "@" not in message:
            kwargs["parse_mode"] = "markdown"      
        return await self.telebot.sendMessage(self.chat_id, message, **kwargs)

    async def sendAnimation(self, animation, **kwargs):
        return await self.telebot.sendAnimation(self.chat_id, animation=animation, duration=30, width=80, height=18)


class MessageInvoker(Invoker):
    def __init__(self, app, r):
        self.app = app
        self.telebot = app["telebot"]
        self.r = r
        self.chat_id = r["message"]["chat"]["id"]
        self.game = app["games"].get(self.chat_id, None)
        self.message = r["message"].get("text", "")
        self.usr = r["message"]["from"]
        self.usr_id = r["message"]["from"]["id"]
        self.usr_first_name = r["message"]["from"]["first_name"]
        self.usr_last_name = r["message"]["from"]["last_name"]
        self.usr_username = r["message"]["from"]["username"]
        self.usr_name = f"{self.usr_first_name} {self.usr_last_name}"
        self.usr_notify = f"@{self.usr_username} {self.usr_first_name}"
        self.method_to_call = self.blank_mock
        if self.message.lower()[:1] == "/":
            self.method_to_call = getattr(self, 'cmd____' + self.message.lower()[1:], None)
            if not self.method_to_call:
                self.method_to_call = self._cmd_404
        return
    
    async def _cmd_404(self):
        return await self.sendMessage(f"Неизвестная команда *{self.message.lower()}*")

    async def cmd____start(self):
        return await self.sendMessage(f"Привет! Напиши `/play` если хочешь поиграть со мной)")

    async def cmd____play(self):
        # ----------- нельзя играть одному ---------------
        if self.chat_id > 0:
            return await self.sendMessage(f"{self.usr_first_name}, игру можно создать только в групповом чате не менее, чем на 4 человек.")
        # ----------- нельзя пересоздавать ---------------
        if self.game:
            # ----------- уже в игре ---------------
            if self.usr_id in self.game["players"]:
                return await self.sendMessage(f"{self.usr_notify}, Ты уже в игре. Подожди!")            
            # ----------- еще не в игре ---------------
            return await self.sendMessage(
                f"{self.usr_notify}, игра уже создаётся в этом чате. Присоединяйся!",
                reply_markup={"inline_keyboard": [[{"text": "✅ Присоединиться", "callback_data": "play:join"}]]}
            )            
        # ----------- создаём игру на этот групповой чат ---------------
        self.app["games"][self.chat_id] = {
            "creator": self.usr_id,
            "players": {self.usr_id: self.usr}
        }
        await self.sendMessage(
            f"*{self.usr_name}* желает начать новую игру.",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "✅ Присоединиться", "callback_data": "play:join"},
                    {"text": "🛑 Отказаться", "callback_data": "play:decline"}
                ]]
            } 
        )
        await self.sendAnimation("https://eva-bot.ru/__res__/small_timer_00_30.gif")
        return None


class CallbackInvoker(Invoker):
    def __init__(self, app, r):
        self.app = app
        self.telebot = app["telebot"]
        self.r = r        
        self.chat_id = r["callback_query"]["message"]["chat"]["id"]
        self.game = app["games"].get(self.chat_id, {"players": dict()})       
        self.callback_data = r["callback_query"]["data"]
        self.usr = r["callback_query"]["from"]
        self.usr_id = r["callback_query"]["from"]["id"]
        self.usr_first_name = r["callback_query"]["from"]["first_name"]
        self.usr_last_name = r["callback_query"]["from"]["last_name"]
        self.usr_username = r["callback_query"]["from"]["username"]
        self.usr_name = f"{self.usr_first_name} {self.usr_last_name}"
        self.usr_notify = f"@{self.usr_username} {self.usr_first_name}" 
        self.method_to_call = self.blank_mock               
        if self.callback_data:
            self.method_to_call = getattr(self, 'callback____' + self.callback_data.replace(":", "____"), None)
            if not self.method_to_call:
                self.method_to_call = self._callback_404
        return

    async def _callback_404(self):
        return await self.sendMessage(f"Неизвестный колбек `{self.callback_data}`")

    async def callback____play____join(self):
        self.game["players"][self.usr_id] = self.usr
        return await self.sendMessage(f"✅ *{self.usr_name}* в игре.")

    async def callback____play____decline(self):
        if self.usr_id in self.game["players"]:
            del self.game["players"][self.usr_id]
        return await self.sendMessage(f"_{self.usr_name} отказался._")



    






