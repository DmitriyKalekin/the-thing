import asyncio
from app.player import Player
from app.card import Card
# from app.misc import chunks
# from app.deck_normal import game_info
# from app.board import Board
# from app.telebot import Callback, User
from random import choice  


class GameView:
    def __init__(self, game):
        self.game = game
        self.t = game.app["telebot"]
        self.cfg = game.app["cfg"]
        self.group_chat_id = self.game.group_chat_id

    def init(self):
        self.board = self.game.board

    async def show_cards_to_all(self):
        if self.cfg.DEBUG:
            for p in self.board.players:
                await self.show_cards(p)
        else:
            await asyncio.gather(*[self.show_cards(p) for p in self.board.players])        

    async def show_cards(self, p: Player):
        # if not p.title_message_id:
        #     r1 = await self.t.sendMessage(p.user_id, f"Ваше имя: *{p.user_fullname}* -------------------------------- ")
        #     p.title_message_id = r1["result"]["message_id"]
        
        if not p.table_message_id:
            r2 = await self.t.sendMessage(p.user_id, self.print_hands(p))
            p.table_message_id = r2["result"]["message_id"]
        
        if not p.hand_slots or len(p.hand_slots) == 0:
            await self.create_image_slots(p)
        else:
            await self.update_image_slots(p)
        
        if not p.panel_message_id:
            r3 = await self.t.sendMessage(p.user_id, f"`[Это сообщение обновится, и вы выберете ваше действие с картами]`")
            p.panel_message_id = r3["result"]["message_id"]
        else:
            await self.t.editMessageText(p.user_id, p.panel_message_id, "\r\n".join(p.local_log))
     
        return

    async def show_play_drop_options(self, p):
        await self.t.editMessageText(
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

    async def show_player_target(self, p, card: Card):
        assert type(card.person_target) == list

        candidates = []
        for pt in card.person_target:
            if pt == "self":
                if not p.is_quarantined():
                    candidates.append(p)
            if pt == "next":
                next_player = self.game.board.player_next(p)
                if not p.is_quarantined() and not next_player.is_quarantined():
                    candidates.append(next_player)
            if pt == "prev":
                prev_player = self.game.board.player_prev(p)
                if not p.is_quarantined() and not prev_player.is_quarantined():
                    candidates.append(prev_player)

        await self.t.editMessageText(
            p.user_id,
            p.panel_message_id,
            "\r\n".join(p.local_log),
            reply_markup={
                "inline_keyboard": [
                    *[[{"text": f"🎯 {p.name}", "callback_data": f"phase2:play_card/player {p.uuid}"}] for p in candidates],
                ]
                # 🖐  🕹 Joystick 🗑 Wastebasket ☣ Biohazard 🎮 🎯 Direct Hit
            },
            parse_mode="markdown"  
        )        


    async def show_give_options(self, p, receiver, can_def=False):
        def_buttons = []
        if can_def:
            def_buttons = [[{"text": f"🛡 {block_card.name}", "callback_data": f"phase3:block_exchange_card {block_card.uuid}"}] for block_card in p.get_possible_block_exchange()]

        await self.t.editMessageText(
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
        return await self.t.sendMessage(self.group_chat_id, msg, **kwargs)

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
        await self.t.editMessageText(p.user_id, p.log_message_id, "\n".join(self.log))        

    async def create_image_slots(self, p):
        """
        Создаём слоты для изображений 
        """
        top_card_image = "https://eva-bot.ru/res/normal/min/top-card-950x1343-min.png"
        media = list([f"https://eva-bot.ru/res/normal/min/{choice(h.images)}-950x1343-min.png" for h in p.hand])
        if len(media) < 5:
            media.append(top_card_image)
        
        r2 = await self.t.sendMediaGroup(p.user_id, list([{"type": "photo", "media": image} for image in media]))
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
                self.game.app.loop.create_task(
                    self.t.editMessageMedia(p.user_id, p.hand_slots[counter], {"type": "photo", "media": image})
                )
            except Warning:
                print(f"Изображение карты осталось старым: {card.name}")
            counter += 1
        
        for i in range(counter, len(p.hand_slots)):
            image = "https://eva-bot.ru/res/normal/min/top-card-950x1343-min.png"
            try:
                self.game.app.loop.create_task(
                    self.t.editMessageMedia(p.user_id, p.hand_slots[counter], {"type": "photo", "media": image})
                )
            except Warning:
                print(f"Изображение осталось старым: top-card")            

    def print_hands(self, player: Player):
        output = f"Ход {self.board.move}, ходит *{self.board.current_player.user_fullname}* \r\n"
        for i, p in enumerate(self.board.players):
            turn = "✅" if i == self.board.turn else "⏳"  # ☣️ # 🤢
            # output += "```"
            name = f"*{p.name}*" if p == self.board.current_player else p.name
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

    async def show_table_to_all(self):
        assert type(self.board.players) == list
        await asyncio.gather(*[self.show_table(p) for p in self.board.players])
        return  

    async def show_table(self, p: Player):
        try:
            await self.t.editMessageText(p.user_id, p.table_message_id, self.print_hands(p))
        except Warning:
            print("Стол остался прежним")