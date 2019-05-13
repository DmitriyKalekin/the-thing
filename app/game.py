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
        self.channels = []
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
        await asyncio.sleep(0)
        return

    def add_player(self, player_id):
        if player_id not in self.channels:
            self.channels.append(player_id)

    def can_start(self) -> bool:
        return True  # TODO: delete
        return len(self.channels) >= Game.MIN_PLAYERS

    async def start(self):
        if not self.can_start():
            await self.print_group(f"Игра отменена. Требуется минимум {Game.MIN_PLAYERS} игроков")
            self.app["events"].unsubscribe_callback(self.group_chat_id)
            for p in self.channels:
                self.app["events"].unsubscribe_callback(p.user_id, self)    
            return
        await self.print_group(game_info["description"] + game_info["on_start_tip"])        
        if self.app["cfg"].DEBUG:
            self.channels = [
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
        self.board = Board(self.channels)
        for p in self.board.players:
            assert type(p) == Player
            self.app["events"].subscribe_callback(p.user_id, self)
        await self.run()

    # TODO: ------------------------------- refactor -------------------

    async def show_cards_to_all(self):
        if self.app["cfg"].DEBUG:
            for p in self.board.players:
                await self.show_cards(p)
        else:
            await asyncio.gather(*[self.show_cards(p) for p in self.board.players])
            
    async def show_cards(self, p: Player):
        # if not p.title_message_id:
        #     r1 = await self.app["telebot"].sendMessage(p.user_id, f"Ваше имя: *{p.user_fullname}* -------------------------------- ")
        #     p.title_message_id = r1["result"]["message_id"]
        
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
        else:
            await self.app["telebot"].editMessageText(p.user_id, p.panel_message_id, "\r\n".join(p.local_log))
        
        if not p.log_message_id:
            r4 = await self.app["telebot"].sendMessage(p.user_id, "\n".join(self.log))
            p.log_message_id = r4["result"]["message_id"]        
        return

    async def show_play_drop_options(self, p):
        await self.app["telebot"].editMessageText(
            p.user_id,
            p.panel_message_id,
            "\r\n".join(p.local_log),
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"▶️ {play_card.name}", "callback_data": f"phase2:play_card {play_card.uuid}"}] for play_card in p.get_possible_play()],
                    *[[{"text": f"🗑 {drop_card.name}", "callback_data": f"phase2:drop_card {drop_card.uuid}"}] for drop_card in p.get_possible_drop()]
                ]
                # 🖐  🕹 Joystick 🗑 Wastebasket ☣ Biohazard 🎮 🎯 Direct Hit
            },
            parse_mode="markdown"  
        )

    async def show_give_options(self, p, receiver, can_def=False):
        def_buttons = []
        if can_def:
            def_buttons = [[{"text": f"🛡 {block_card.name}", "callback_data": f"phase3:block_exchange_card {block_card.uuid}"}] for block_card in p.get_possible_block_exchange()]

        await self.app["telebot"].editMessageText(
            p.user_id,
            p.panel_message_id,
            "\r\n".join(p.local_log),
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"🎁 {give_card.name}", "callback_data": f"phase3:give_card {give_card.uuid}"}] for give_card in p.get_possible_give(receiver)],
                    *def_buttons
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
            events = self.callback_input[p.user_id]
            index = None
            for i, clb in enumerate(events):
                if clb.message_id == p.panel_message_id:
                    index = i
            if index is not None:
                c = self.callback_input[p.user_id].pop(index)
                return c.data, p

    async def clear_input(self, p: Player):
        assert p.panel_message_id is not None
        return await self.app["telebot"].editMessageText(p.user_id, p.panel_message_id, "\r\n".join(p.local_log))       

    async def show_table_to_all(self, table):
        assert type(self.board.players) == list
        await asyncio.gather(*[self.show_table(p, table) for p in self.board.players])
        return  

    async def show_table(self, p: Player, table: str):
        try:
            await self.app["telebot"].editMessageText(p.user_id, p.table_message_id, table)
        except Warning:
            print("Стол остался прежним")

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
                print(f"Изображение карты осталось старым: {card.name}")
            counter += 1
        
        for i in range(counter, len(p.hand_slots)):
            image = "https://eva-bot.ru/res/normal/min/top-card-950x1343-min.png"
            try:
                self.app.loop.create_task(
                    self.app["telebot"].editMessageMedia(p.user_id, p.hand_slots[counter], {"type": "photo", "media": image})
                )
            except Warning:
                print(f"Изображение осталось старым: top-card")            

    def print_hands(self):
        output = f"Ход {self.board.move}, ходит *{self.board.current_player().user_fullname}* \r\n"
        for i, p in enumerate(self.board.players):
            turn = "✅" if i == self.board.turn else "⏳"  # ☣️ # 🤢
            # output += "```"
            name = f"*{p.name}*" if p == self.board.current_player() else p.name
            output += f"{turn} {p.avatar} {name}\r\n" 
            # output += "```"            
            # for o in p.get_cards_names():
            #     if o == "Заражение":
            #         output += "`[`🤢`" + o + "]`; "                                    
            #     if o == "Нечто":
            #         output += "`[`🍄`" + o + "]`; "
            #     else:
            #         output += "`[" + o + "]`; "
            if len(p.global_log) > 0:
                output += '\r\n'.join([f"             `{s}`" for s in p.global_log]) + "\r\n"
            else:
                output += "`       ...`\r\n"
        return output        

    async def phase1(self, p: Player) -> bool:
        """
        Фаза взятия карты и игры паники
        Возвращает необходимость продолжать код
        """
        # p.global_log = "тянет карту с колоды..."
        # await self.show_table_to_all()
        # await self.show_log_to_all(f"Фаза 1. {p.user_fullname} тянет карту с колоды")
        card = p.pull_deck()
        assert type(card) == Card
        if not card.is_panic():
            p.take_on_hand(card)
            p.local_log.append(f"🎲 событие `{card.name}` c колоды")
            p.global_log.append(f"🎲 Вытянул событие из колоды")
            await self.show_cards(p)
            return True
        else:
            p.local_log.append(f"🔥 паника `{card.name}` с колоды, ход завершён.")
            p.global_log.append(f"🔥 Вытянул панику `{card.name}` с колоды. Ход завершён.")
            p.play_panic(card)
            self.board.deck.append(card)  # карта паники ушла в колоду
            return False
        return True

    async def phase2(self, p: Player):
        """
        Фаза сброса или игры карты с руки
        """
        # Обновили карты на руке игрока и ждём от него хода
        # await self.show_cards(p)
        p.local_log.append(f"❗️ Сыграйте ▶️ или сбросьте 🗑 карту...")
        p.global_log.append(f"🃏 Играет или сбрасывает...")
        await asyncio.gather(*[
            self.show_play_drop_options(p),
            self.show_table_to_all(self.print_hands())
        ])

        cmd = None
        # while cmd not in ["phase2:play_card", "phase2:drop_card"]:
        # await asyncio.sleep(0)
        full_input, triggered_player = await self.listen_input(p)
        cmd, card_uuid = full_input.split(" ")
        assert cmd == "phase2:play_card" or cmd == "phase2:drop_card"
        assert triggered_player == p
        card = p.pop_card_by_uuid(int(card_uuid))  # выбранная карта
        assert type(card) == Card
        if cmd == "phase2:play_card":
            p.play_card(card, target=None)
            p.local_log[-1] = f"▶️ сыграна `{card.name}`"
            p.global_log[-1] = f"▶️ Сыграл карту `{card.name}`"
        else:
            p.local_log[-1] = f"🗑 сброшена `{card.name}`"   
            p.global_log[-1] = f"🗑 Сбросил карту"
      
        await self.clear_input(p)
        
        p.drop_card(card)  # в любом случае в колоду
        await asyncio.gather(*[
            self.show_cards(p),
            self.show_table_to_all(self.print_hands())
        ])
        return

    async def proccess_exchange(self, p: Player, next_player: Player):
        full_input, player = await self.listen_input(p)
        assert player == p
        cmd, card_uuid = full_input.split(" ")
        # BUG: assertion error here
        assert cmd in ["phase3:give_card", "phase3:block_exchange_card"]
        my_card = player.pop_card_by_uuid(int(card_uuid))
        assert type(my_card) == Card

        if cmd == "phase3:give_card":
            player.local_log[-1] = f"🎁 отдана `{my_card.name}` для *{next_player.user_fullname}*"        
            player.global_log[-1] = f"♣️ Отдал карту для {next_player.user_fullname}"

            await asyncio.gather(*[
                self.clear_input(player),
                self.show_cards(player),
                self.show_table_to_all(self.print_hands())
            ])
        else:
            assert cmd == "phase3:block_exchange_card"
            player.local_log[-1] = f"🛡 сыграна защита `{my_card.name}` от *{next_player.user_fullname}*"        
            player.global_log[-1] = f"🛡 Защитился `{my_card.name}` от обмена с {next_player.user_fullname}"

            await asyncio.gather(*[
                self.clear_input(player),
                self.show_cards(player),
                self.show_table_to_all(self.print_hands())
            ])            
        return player, my_card

    async def phase3(self, p: Player):
        next_player = self.board.player_next()
        p.local_log.append(f"❗️ Передайте карту *{next_player.user_fullname}*")
        p.global_log.append(f"💤 Передаёт карту {next_player.user_fullname}")

        next_player.local_log.append(f"❗️ Передайте карту *{p.user_fullname}*, либо защититесь 🛡 от обмена.")
        next_player.global_log.append(f"💤 Передаёт карту {p.user_fullname}")

        exchangers = await asyncio.gather(*[
            self.show_give_options(p, next_player),
            self.show_give_options(next_player, p, can_def=True),
            self.show_table_to_all(self.print_hands()),
            self.proccess_exchange(p, next_player),
            self.proccess_exchange(next_player, p)
        ])
        p1, card1 = exchangers[3]
        p2, card2 = exchangers[4]
        assert type(p1) == Player
        assert type(p2) == Player
        assert type(card1) == Card
        assert type(card2) == Card
        p1.take_on_hand(card2, sender=p2)
        p2.take_on_hand(card1, sender=p1)

        p1.local_log.append(f"🤲 получена `{card2.name}` от *{p2.user_fullname}*")
        p2.local_log.append(f"🤲 получена `{card1.name}` от *{p1.user_fullname}*")
        p1.global_log[-1] = f"👌🏻 Передал карту {p2.user_fullname}"
        p2.global_log[-1] = f"👌🏻 Передал карту {p1.user_fullname}"

        await asyncio.gather(*[
            self.app.loop.create_task(self.show_cards(p1)),
            self.app.loop.create_task(self.show_cards(p2)),
            self.app.loop.create_task(self.show_table_to_all(self.print_hands()))
        ])
        return

    async def run(self):
        # До старта игры показываем карты игрокам, пишем историю ситуации и ждём, чтобы они прочитали
        p = None
        await self.show_cards_to_all()
        while not self.board.is_end:
            await asyncio.sleep(0)
            
            if p:
                p.global_log = []
                p.local_log.append("`----------`")
                if len(p.local_log) > 10:
                    for _ in range(0, 5):
                        p.local_log.pop(0)

            self.board.next_turn()    
            p = self.board.current_player()

            # Рисуем стол и очередность в общем чате
            await self.show_table_to_all(self.print_hands())
            # await self.print_group(self.table)
            # Тянем карту: либо паника и переход хода, либо фаза сыграть карту с руки
            p.global_log = []
            if len(p.local_log) > 0:
                p.local_log.append("`----------`")

            if not await self.phase1(p):
                print("=============================")
                # self.app.loop.create_task(self.delay_flush(p))
                continue
            await self.phase2(p)
            await self.phase3(p)
            # await self.app.loop.create_task(self.delay_flush(p))
            print("=============================")
        await self.print_group("game ended")
        return
