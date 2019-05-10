import asyncio
from app.player import Player
from app.card import Card
# from app.misc import chunks
from app.deck_normal import game_info
from app.board import Board
from app.telebot import Callback, User
from random import choice       


def list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


class Game:
    MIN_PLAYERS = 4
    STATUS_PENDING = "pending"
    STATUS_LAUNCHED = "launched"
    STATUS_CANCELED = "canceled"

    def __init__(self, group_chat_id, app):
        self.group_chat_id = group_chat_id
        self.players = []
        self.status = Game.STATUS_PENDING
        self.board = None
        self.app = app
        self.app["events"].subscribe_callback(self.group_chat_id, self)
        self.callback_input = dict()
        self.table = "```Здесь отобразится стол```"        
        self.log = ["```Здесь лог событий```"]

    async def update_callback(self, callback: Callback):
        assert type(callback.sender) == User
        if callback.chat_id not in self.callback_input:
            self.callback_input[callback.chat_id] = []    
        self.callback_input[callback.chat_id].append(callback)
        print(f"Game {self.group_chat_id} updated", callback, "SENDER_UUID:", callback.sender.id)
        print("CLB struct:", self.callback_input)
        await asyncio.sleep(0)
        return

    def add_player(self, player_id):
        if player_id not in self.players:
            self.players.append(player_id)

    def can_start(self) -> bool:
        return True  # TODO: delete
        return len(self.players) >= Game.MIN_PLAYERS

    async def start(self):
        if not self.can_start():
            await self.print_group(f"Игра отменена. Требуется минимум {Game.MIN_PLAYERS} игроков")
            self.app["events"].unsubscribe_callback(self.group_chat_id)
            for p in self.players:
                self.app["events"].unsubscribe_callback(p.user_id, self)    
            return
        await self.print_group(game_info["description"] + game_info["on_start_tip"])        
        mock_players = self.players
        # TODO: delete this mock
        mock_players = [
            {
                "group_chat_id": self.group_chat_id,
                "user_id": 435627225,
                "user_fullname": "Дмитрий Калекин",
                "user_alert": "@herr_horror Дмитрий"
            },
            {
                "group_chat_id": self.group_chat_id,
                "user_id": 435627225,
                "user_fullname": "Dmitriy Zaytsev",
                "user_alert": "@1"
            },
            {
                "group_chat_id": self.group_chat_id,
                "user_id": 435627225,
                "user_fullname": "Zag",
                "user_alert": "@2"
            },
            {
                "group_chat_id": self.group_chat_id,
                "user_id": 435627225,
                "user_fullname": "Александр Грицай",
                "user_alert": "@3"
            }                                     
        ]
        self.board = Board(mock_players)

        for p in self.board.players:
            assert type(p) == Player
            self.app["events"].subscribe_callback(p.user_id, self)
        await self.run()

    # TODO: ------------------------------- refactor -------------------

    async def show_cards(self, p):
        if not p.title_message_id:
            r1 = await self.app["telebot"].sendMessage(p.user_id, f"Ваше имя: *{p.user_fullname}* -------------------------------- ")
            p.title_message_id = r1["result"]["message_id"]
        
        if not p.table_message_id:
            r2 = await self.app["telebot"].sendMessage(p.user_id, self.table)
            p.table_message_id = r2["result"]["message_id"]
        
        if not p.hand_slots or len(p.hand_slots) == 0:
            await self.create_image_slots(p)
        else:
            await self.update_image_slots(p)
        
        if not p.panel_message_id:
            r3 = await self.app["telebot"].sendMessage(p.user_id, f"`[Это сообщение обновится, и вы выберете ваше действие с картами]`")
            p.panel_message_id = r3["result"]["message_id"]
        
        if not p.log_message_id:
            r4 = await self.app["telebot"].sendMessage(p.user_id, "\n".join(self.log))
            p.log_message_id = r4["result"]["message_id"]        
        return

    async def show_play_drop_options(self, p, msg=""):
        await self.app["telebot"].editMessageText(
            p.user_id,
            p.panel_message_id,
            msg,
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"🎯 {p.get_card_by_uuid(play_uuid).name}", "callback_data": f"phase2:play_card {play_uuid}"}] for play_uuid in p.get_possible_play()],
                    *[[{"text": f"🗑 {p.get_card_by_uuid(drop_uuid).name}", "callback_data": f"phase2:drop_card {drop_uuid}"}] for drop_uuid in p.get_possible_drop()]
                ]
                # 🖐  🕹 Joystick 🗑 Wastebasket ☣ Biohazard 🎮 🎯 Direct Hit
            },
            parse_mode="markdown"  
        )

    async def show_give_options(self, p, receiver, msg=""):
        await self.app["telebot"].editMessageText(
            p.user_id,
            p.panel_message_id,
            msg,
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"🖐 {p.get_card_by_uuid(give_uuid).name}", "callback_data": f"phase3:give_card {give_uuid}"}] for give_uuid in p.get_possible_give(receiver)]
                ]
                #   🕹 Joystick 🗑 Wastebasket ☣ Biohazard 🎮 🎯 Direct Hit
            },
            parse_mode="markdown"  
        )        

    async def print_group(self, msg: str, **kwargs):
        return await self.app["telebot"].sendMessage(self.group_chat_id, msg, **kwargs)

    async def listen_input(self, p: Player):
        while True:
            await asyncio.sleep(1)
            if p.user_id not in self.callback_input:
                continue
            print("user_id inside")
            events = self.callback_input[p.user_id]
            index = None
            print("events =", events)
            for i, clb in enumerate(events):
                if clb.message_id == p.panel_message_id:
                    index = i
            print("index =", index)                    
            if index is not None:
                c = self.callback_input[p.user_id].pop(index)
                print("GOT", c)
                return c.data, p

    async def clear_input(self, p: Player, msg=""):
        assert p.panel_message_id is not None
        return await self.app["telebot"].editMessageText(p.user_id, p.panel_message_id, msg)       

    async def show_cards_to_all(self):
        assert type(self.board.players) == list
        for p in self.board.players:
            await self.show_cards(p)
            # self.app.loop.create_task()
        return

    async def show_table_to_all(self):
        self.table = self.board.print_hands()
        assert type(self.board.players) == list
        for p in self.board.players:
            await self.show_table(p)
            # self.app.loop.create_task(self.show_table(p))
        return  

    async def show_table(self, p: Player):
        try:
            await self.app["telebot"].editMessageText(p.user_id, p.table_message_id, self.table)
        except Warning:
            print("Стол не поменялся")

    async def show_log_to_all(self, msg: str):
        self.log.append(msg)
        while len(self.log) > 6:
            _ = self.log.pop(0)
        assert type(self.board.players) == list
        for p in self.board.players:
            await self.show_log(p)
            # self.app.loop.create_task(self.show_log(p))
        return

    async def show_log(self, p: Player):
        await self.app["telebot"].editMessageText(p.user_id, p.log_message_id, "\n".join(self.log))        

    async def create_image_slots(self, p):
        """
        Создаём слоты для изображений 
        """
        
        top_card_image = "https://eva-bot.ru/res/normal/min/top-card-950x1343-min.png"
        media = list([f"https://eva-bot.ru/res/normal/min/{choice(h.images)}-950x1343-min.png" for h in p.hand])
        if len(media) < 5:
            media.append(top_card_image)
        
        r2 = await self.app["telebot"].sendMediaGroup(p.user_id, list([{"type": "photo", "media": image} for image in media]))
        for i, msg in enumerate(r2["result"]):
            p.hand_slots.append(msg["message_id"])

    async def update_image_slots(self, p):
        """
        Обновляем слоты для изображений -  только изменившиеся
        """
        counter = 0
        for card in p.hand:
            assert type(card) == Card
            image = f"https://eva-bot.ru/res/normal/min/{choice(card.images)}-950x1343-min.png"
            try:
                self.app.loop.create_task(
                    self.app["telebot"].editMessageMedia(p.user_id, p.hand_slots[counter], {"type": "photo", "media": image})
                )
            except Warning:
                print(f"Изображение не поменялось на руке: {card}")
            counter += 1
        
        for i in range(counter, len(p.hand_slots)):
            image = "https://eva-bot.ru/res/normal/min/top-card-950x1343-min.png"
            try:
                self.app.loop.create_task(
                    self.app["telebot"].editMessageMedia(p.user_id, p.hand_slots[counter], {"type": "photo", "media": image})
                )
            except Warning:
                print(f"Изображение не поменялось на руке: top-card")            

    async def choose(self, user_id: int, message: str, options: list):
        # await self.print(channel_id, message)
        await asyncio.sleep(10)
        return "1" 

    async def phase1(self, p: Player) -> bool:
        """
        Фаза взятия карты и игры паники
        Возвращает необходимость продолжать код
        """
        # p.log_state = "тянет карту с колоды..."
        # await self.show_table_to_all()
        # await self.show_log_to_all(f"Фаза 1. {p.user_fullname} тянет карту с колоды")
        card = p.pull_deck()
        assert type(card) == Card
        if not card.is_panic():
            p.take_on_hand(card)
            await self.show_cards(p)
            # await self.show_log_to_all(f"Добавлена на руку карта события: {card.name}. Теперь нужно сыграть карту или сбросить.")
            return True
        else:
            await self.show_log_to_all(f"{p.user_fullname} вытянул карту паники {card.name}. Все забегали. Переход хода")
            p.play_panic(card)
            self.board.deck.append(card)  # карта паники ушла в колоду
            p.log_state = "вытянул панику, закончил ход"
            return False
        return True

    async def phase2(self, p: Player):
        """
        Фаза сброса или игры карты с руки
        """
        # Обновили карты на руке игрока и ждём от него хода
        # await self.show_cards(p)
        p.log_state = "вытянул карту: играет или сбрасывает..."
        # await self.show_log_to_all(f"Фаза 2. *{p.user_fullname}* играет или сбрасывает карту")
        await self.show_play_drop_options(p, "Сыграйте или сбросьте карту")
        await self.show_table_to_all()

        cmd = None
        # while cmd not in ["phase2:play_card", "phase2:drop_card"]:
        # await asyncio.sleep(0)
        full_input, triggered_player = await self.listen_input(p)
        print("Получен triggered_player", triggered_player)
        cmd, card_uuid = full_input.split(" ")
        assert cmd == "phase2:play_card" or cmd == "phase2:drop_card"
        assert triggered_player == p
        print("received", cmd, card_uuid)
        card = p.pop_card_by_uuid(int(card_uuid))  # выбранная карта
        assert type(card) == Card
        if cmd == "phase2:play_card":
            p.play_card(card, target=None)
            p.log_state = f"сыграл карту {card.name}"
            await self.clear_input(p, f"Вы сыграли карту {card.name}")
            await self.show_log_to_all(f"*{p.user_fullname}* играет карту {card.name}")
        else:
            p.log_state = f"сбросил карту"
            await self.clear_input(p, f"Вы сбросили карту {card.name}")
            await self.show_log_to_all(f"*{p.user_fullname}* сбрасывает карту {card.name}")
        
        p.drop_card(card)  # в любом случае в колоду
        await self.show_cards(p)
        await self.show_table_to_all()
        return

    async def phase3(self, p: Player):
        next_player = self.board.player_next()
        p.log_state = f"меняется картой с {next_player.user_fullname}"
        next_player.log_state = f"меняется картой с {p.user_fullname}"
        # await self.show_log_to_all(f"Фаза 3. Обмен картами со следующим игроком. Меняются *{p.user_fullname}* и *{next_player.user_fullname}*")
        await self.show_give_options(p, next_player, f"*{next_player.user_fullname}* должен получить от вас одну карту. Выбирайте!")
        await self.show_give_options(next_player, p, f"*{p.user_fullname}* должен получить от вас одну карту, либо защититесь от обмена защитной картой с руки. Выбирайте!")
        await self.show_table_to_all()

        full_input, triggered_player1 = await self.listen_input(p)
        cmd, card_uuid = full_input.split(" ")
        assert cmd == "phase3:give_card"
        my_card = triggered_player1.pop_card_by_uuid(int(card_uuid))
        assert type(my_card) == Card
        triggered_player1.log_state = f"поменялся картой"
        await self.clear_input(triggered_player1, f"Вы отдали карту {my_card.name}")
        await self.show_cards(triggered_player1)
        await self.show_table_to_all()

        full_input, triggered_player2 = await self.listen_input(next_player)
        cmd, card_uuid = full_input.split(" ")
        assert cmd == "phase3:give_card"
        his_card = triggered_player2.pop_card_by_uuid(int(card_uuid))
        assert type(his_card) == Card
        triggered_player2.log_state = f"поменялся картой"
        await self.clear_input(triggered_player2, f"Вы отдали карту {his_card.name}")
        await self.show_cards(triggered_player2)
        await self.show_table_to_all()

        triggered_player1.take_on_hand(his_card)
        triggered_player2.take_on_hand(my_card)
        await self.show_cards(triggered_player1)
        await self.show_cards(triggered_player2)
        await self.show_table_to_all()
        return

    async def run(self):
        # До старта игры показываем карты игрокам, пишем историю ситуации и ждём, чтобы они прочитали
        await self.show_cards_to_all()
        await asyncio.sleep(0)

        while not self.board.is_end:
            self.board.next_turn()
            p = self.board.current_player()
            # Рисуем стол и очередность в общем чате
            self.table = self.board.print_hands()
            await self.show_table_to_all()
            # await self.print_group(self.table)
            # Тянем карту: либо паника и переход хода, либо фаза сыграть карту с руки
            if not await self.phase1(p):
                continue
            await self.phase2(p)
            await self.phase3(p)
        await self.print_group("game ended")
        return
