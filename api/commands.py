import json
import pymysql
import time
import threading

class CommandsRouter:
    """
    """
    def __init__(self, app):
        self.app = app
        self.telebot = app["telebot"]

    
    async def index_message(self, r):
        """
        """
        print("INSIDE MSG")
        chat_id = r["message"]["chat"]["id"]
        message = r["message"].get("text", "")
        sender = r["message"]["from"]["id"]
        
        if message.lower()[:1]=="/":
            method_to_call = getattr(self, 'cmd____'+message.lower()[1:], None)
            if method_to_call:
                return await method_to_call(chat_id, message, sender, r)
            else:
                return await self.telebot.sendMessage(chat_id, f"Неизвестная команда *{message.lower()}*", parse_mode="markdown")  
        return   

    
    async def index_callback(self, r):
        """
        """
        chat_id = r["callback_query"]["message"]["chat"]["id"]
        callback_data = r["callback_query"]["data"]
        sender = r["callback_query"]["from"]["id"]
        
        print("CHAT_ID", chat_id)
        print("callback_data", callback_data)
        print("sender", sender)

        if callback_data:
                method_to_call = getattr(self, 'callback____'+callback_data.replace(":", "____"), None)
                if method_to_call:
                    return await method_to_call(chat_id, r)
                else:
                    return await self.telebot.sendMessage(chat_id, f"Неизвестный колбек: *{callback_data}*", parse_mode="markdown")
        return     

    async def cmd____play(self, chat_id, message, sender, r):
        """
        """
        print("INSIDE PLAY")
        sender_first_name = r["message"]["from"]["first_name"]
        sender_username = r["message"]["from"]["username"]
        sender_name = r["message"]["from"]["first_name"] + " " + r["message"]["from"]["last_name"]

        # ----------- нельзя играть одному ---------------
        if chat_id > 0:
            await self.telebot.sendMessage(chat_id, f"{sender_first_name}, игру можно создать только в групповом чате не менее, чем на 4 человек.")
            return None

        # ----------- нельзя пересоздавать ---------------
        if chat_id in self.app["games"]:
            # ----------- уже в игре ---------------
            if r["message"]["from"]["id"] in self.app["games"][chat_id]["players"]:
                await self.telebot.sendMessage(chat_id, f"@{sender_username} {sender_first_name}, Ты уже в игре. Подожди!")            
                return None 

            # ----------- еще не в игре ---------------
            await self.telebot.sendMessage(chat_id, f"@{sender_username} {sender_first_name}, игра уже создаётся в этом чате. Присоединяйся!",
            reply_markup = {
                "inline_keyboard" :    
                        [[{"text":"✅ Присоединиться","callback_data":"play:join"}]] 
            })            
            return None

        # ----------- создаём игру на этот групповой чат ---------------
        self.app["games"][chat_id] = {
            "creator": r["message"]["from"]["id"],
            "players": {r["message"]["from"]["id"]: r["message"]["from"]}
        }

        await self.telebot.sendMessage(chat_id, f"*{sender_name}* желает начать новую игру.", parse_mode="markdown",
        reply_markup = {
            "inline_keyboard" :    
                    [[{"text":"✅ Присоединиться","callback_data":"play:join"},{"text":"🛑 Отказаться","callback_data":"play:decline"}]] 
        })
        await self.telebot.sendAnimation(chat_id, animation="https://eva-bot.ru/__res__/small_timer_00_30.gif", duration=30, width=80, height=18) #, caption="<b>Таймер</b>", parse_mode="html"
        return None    


    async def callback____play____join(self, chat_id, r):
        self.app["games"][chat_id]["players"][r["callback_query"]["from"]["id"]] = r["callback_query"]["from"]
        sender_name = r["callback_query"]["from"]["first_name"] + " " + r["callback_query"]["from"]["last_name"]
        return await self.telebot.sendMessage(chat_id, f"✅ *{sender_name}* в игре.", parse_mode="markdown")

    async def callback____play____decline(self, chat_id, r):
        if r["callback_query"]["from"]["id"] in self.app["games"][chat_id]["players"]:
            del self.app["games"][chat_id]["players"][r["callback_query"]["from"]["id"]]
        sender_name = r["callback_query"]["from"]["first_name"] + " " + r["callback_query"]["from"]["last_name"]
        return await self.telebot.sendMessage(chat_id, f"_{sender_name} отказался._", parse_mode="markdown")

# -----------------------------------------------------------------------------------             
    
    # def worker(self, chat_id, ans):
    #     r = TeleBot.sendMessage(chat_id,  "У вас: 60 секунд", parse_mode="markdown")

    #     for s in range(59, 0, -1):
    #         if (s % 10 == 0) or (s < 10):
    #             TeleBot.editMessageText(
    #             chat_id, 
    #             r["result"]["message_id"],
    #             f"У вас: {s} секунд",
    #             parse_mode="markdown"
    #             )
    #         time.sleep(1)
        
    #     TeleBot.editMessageText(chat_id, r["result"]["message_id"], ans, parse_mode="markdown")
        
        # TeleBot.sendMessage(chat_id, "Прекратите обсуждение! Я готов принять ваш ответ.", parse_mode="markdown")
        # time.sleep(5)
        # TeleBot.sendMessage(chat_id,  , parse_mode="markdown")


    






