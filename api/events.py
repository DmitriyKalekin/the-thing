import asyncio
from game.board import Game
from random import choice
from pprint import pprint
import traceback


class EventsInvoker:
    def __init__(self):
        self.events = []

    def set_application(self, app):
        self.app = app

    def g(self, chat_id) -> Game:
        return self.app["games"].get_game(chat_id)

    async def fire_event(self, name, params: dict):
        self.events.append({"name": name, **params})
        return

    async def invoke(self, e: dict):
        method_name = e.get("name", "")
        method_to_call = getattr(self, 'event____' + method_name, None) 
        if not method_to_call:
            print(f"ERROR: неизвестное событие: {method_name}")
            return
        del e["name"]
        print(f"Получено событие: {method_name}")
        return await method_to_call(**e)

    async def event____create_game(self, chat_id=0, usr_id=None):
        assert chat_id < 0
        assert usr_id > 0
        print(f"Создана или существует игра в {chat_id}")
        self.g(chat_id).add_player(usr_id)
        return 
    
    async def event____join_game(self, chat_id=0, usr_id=None, usr_fullname=None, usr_alert=None):
        assert chat_id < 0
        assert usr_id > 0
        print(f"Игрок присоединился в {chat_id}")
        game = self.g(chat_id)
        # войти можно только в неначатую игру
        if game.status == Game.STATUS_PENDING:
            self.g(chat_id).add_player({"usr_id": usr_id, "chat_id": chat_id, "usr_fullname": usr_fullname, "usr_alert": usr_alert})
        return

    async def event____game_started(self, chat_id=0):
        assert chat_id < 0
        if not self.g(chat_id).can_start() and chat_id != -272083086:
            self.g(chat_id).status = Game.STATUS_CANCELED
            await self.self.print(chat_id, "Не набрали необходимое количество человек (4). Игра отменена.")
            return
        
        self.g(chat_id).status = Game.STATUS_LAUNCHED
        self.g(chat_id).create_board()
        await self.g(chat_id).run()
        await self.print(chat_id, "Игра началась")

    async def print(self, channel_id: int, message: str):
        return await self.app["telebot"].sendMessage(channel_id, message, parse_mode="markdown")

    async def input(self, channel_id: int, message: str):
        # await self.print(channel_id, message)
        await asyncio.sleep(10)
        return "1"

    async def update_players_hands(self, players: list):
        for p in players:
            await self.show_cards(p)
            break
        return

    async def create_image_slots(self, p):
        """
        Создаём слоты для изображений 
        """
        top_card_image = "https://eva-bot.ru/res/normal/top-card-950x1343.png"
        media = list([f"https://eva-bot.ru/res/normal/{choice(h.images)}-950x1343.png" for h in p.hand])
        if len(media) < 5:
            media.append(top_card_image)
        r2 = await self.app["telebot"].sendMediaGroup(p.usr_id, list([{"type": "photo", "media": image} for image in media]))
        for i, msg in enumerate(r2["result"]):
            if i == 4:
                p.hand_message_id.append({"message_id": msg["message_id"], "card_uuid": 32768})
            else:
                p.hand_message_id.append({"message_id": msg["message_id"], "card_uuid": p.hand[i].uuid})

    async def update_image_slots(self, p):
        """
        Обновляем слоты для изображений -  только изменившиеся
        """
        top_card_image = "https://eva-bot.ru/res/normal/top-card-950x1343.png"
        # Доступные слоты на панели руки, куда можно положить изображение новой карты
        awailable_slots = []
        # Карты, которые надо нарисовать на этих слотах - будем исключать из имеющихся
        cards_to_paint = list([c.uuid for c in p.hand])
        # print("--------------исключаю карты-----------------")
        # pprint(cards_to_paint)
        for i, place_on_hand in enumerate(p.hand_message_id):
            # print("На итерации:")
            # pprint(place_on_hand)
            card = p.get_card_by_uuid(place_on_hand["card_uuid"])
            if card and card.uuid == p.hand[i].uuid:
                cards_to_paint.remove(p.hand[i].uuid)
                continue
            awailable_slots.append(place_on_hand)
        # pprint(p.hand)
        # pprint(awailable_slots)
        # print(f"Свободных слотов {len(awailable_slots)}, карт на отрисовку {len(cards_to_paint)}")
        for i in range(0, max(len(cards_to_paint), len(awailable_slots))):
            card = p.get_card_by_uuid(cards_to_paint[i])
            if card:
                await self.app["telebot"].editMessageMedia(p.usr_id, awailable_slots[i]["message_id"], {"type": "photo", "media": f"https://eva-bot.ru/res/normal/{choice(card.images)}-950x1343.png"})
            else:
                await self.app["telebot"].editMessageMedia(p.usr_id, awailable_slots[i]["message_id"], {"type": "photo", "media": top_card_image})

    async def show_cards(self, p):
        if not p.title_message_id:
            r1 = await self.app["telebot"].sendMessage(p.usr_id, f"Ваше имя: *{p.usr_fullname}*", parse_mode="markdown")
            p.title_message_id = r1["result"]["message_id"]
        if not p.hand_message_id:
            await self.create_image_slots(p)
        else:
            await self.update_image_slots(p)
        if not p.panel_message_id:
            r3 = await self.app["telebot"].sendMessage(p.usr_id, f"`[Это сообщение обновится, и вы выберете ваше действие с картами]`", parse_mode="markdown")
            p.panel_message_id = r3["result"]["message_id"]
        return

    async def show_play_drop_options(self, p):
        await self.app["telebot"].editMessageText(
            p.usr_id,
            p.panel_message_id,
            "Вы можете сыграть карту с руки или сбросить",
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"🎯 {p.get_card_by_uuid(play_uuid).name}", "callback_data": f"phase2:play_card {play_uuid}"}] for play_uuid in p.get_possible_play()],
                    *[[{"text": f"🗑 {p.get_card_by_uuid(drop_uuid).name}", "callback_data": f"phase2:drop_card {drop_uuid}"}] for drop_uuid in p.get_possible_drop()]
                ]
                # 🖐  🕹 Joystick 🗑 Wastebasket ☣ Biohazard 🎮 🎯 Direct Hit
            },
            parse_mode="markdown"  
        )
        await asyncio.sleep(10)
        return "1"         

    async def choose(self, user_id: int, message: str, options: list):
        # await self.print(channel_id, message)
        await asyncio.sleep(10)
        return "1"        

    async def listen(self):
        """
        """
        while True:
            for e in self.events:
                await self.invoke(e)
            await asyncio.sleep(1)
        return