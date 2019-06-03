import asyncio
from app.player import Player
from app.card import Card, IPlayableToPerson
# from app.misc import chunks
# from app.deck_normal import game_info
# from app.board import Board
# from app.telebot import Callback, User
from random import choice  
import traceback
from pprint import pprint

class TestView:
    def init(self, game):
        self.game = game
        self.board = self.game.board
        self.cfg = game.app["cfg"]
        self.group_chat_id = self.game.group_chat_id

    def print_hands(self, player: Player):
        output = "-----------------------------------"
        output += f"Ход {self.board.move}, ходит *{self.board.current_player.user_fullname}* \r\n"
        for i, p in enumerate(self.board.players):
            turn = "✅" if i == self.board.current_player == p else " "  # ☣️ # 🤢
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

    async def print_group(self, msg: str, **kwargs):
        return print(msg, **kwargs)

    async def show_cards_to_all(self):
        # TODO: gather
        if self.cfg.DEBUG:
            for p in self.board.players:
                await self.show_cards(p)
        else:
            await asyncio.wait([self.show_cards(p) for p in self.board.players])         


    async def show_cards(self, p: Player):
        print(f"Показываю карты игроку: {p.name}")
        if not p.table_message_id:
            print(p.user_id, self.print_hands(p))
            p.table_message_id = 1111
        
        await self.update_image_slots(p)
        
        if not p.panel_message_id:
            p.panel_message_id = 2222
        else:
            print(p.user_id, p.panel_message_id, "\r\n".join(p.local_log))
        return            



    async def update_image_slots(self, p):
        """
        Обновляем слоты для изображений -  только изменившиеся
        """
        print(f"Рука {p.name}:")
        for i, card in enumerate(p.hand):
            print(i+1, card.name)           


    async def show_table_to_all(self):
        assert type(self.board.players) == list
        # print("Отрисовка борды всем")
        # traceback.print_stack()
        # TODO: gather
        await asyncio.wait([self.show_table(p) for i, p in enumerate(self.board.players) if i==0])
        return  

    async def show_table(self, p: Player):
        try:
            print(p.user_id, p.table_message_id, self.print_hands(p))
        except Warning:
            print("Стол остался прежним")        

    async def show_play_drop_options(self, p: Player):
        play_opts = []
        for play_card in p.get_possible_play():
            candidates = play_card.get_targets(p)
            if len(candidates) > 1:
                label = f"👨x{len(candidates)}"
            else:
                label = f"на 🎯 {candidates[0].name}"
            play_opts.append([{"text": f"▶️ {play_card.name} {label}", "callback_data": f"phase2:play_card {play_card.uuid}"}])

        print(str(p.user_id))
        print(str(p.panel_message_id))
        print("\r\n Локальный лог:".join(p.local_log))
        pprint(play_opts)
        pprint([[{"text": f"🗑 {drop_card.name}", "callback_data": f"phase2:drop_card {drop_card.uuid}"}] for drop_card in p.get_possible_drop()])
