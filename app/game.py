import asyncio
from app.player import Player
# from app.card import Card
# from app.misc import chunks
from app.deck_normal import game_info
from app.board import Board
from app.telebot import Callback, User
# from random import choice    
from app.game_view import GameView   


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
        # self.table = "```Здесь отобразится стол```"        
        self.view = GameView(self)

    async def update_callback(self, callback: Callback):
        assert type(callback.sender) == User
        if callback.chat_id not in self.callback_input:
            self.callback_input[callback.chat_id] = []    
        self.callback_input[callback.chat_id].append(callback)
        await asyncio.sleep(0)
        return

    async def clear_input(self, p: Player):
        assert p.panel_message_id is not None
        return await self.app["telebot"].editMessageText(p.user_id, p.panel_message_id, "\r\n".join(p.local_log)) 

    async def input(self, p: Player):
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
                await self.clear_input(p)
                return c.data.split(" ")        

    def add_player(self, player_id):
        if player_id not in self.channels:
            self.channels.append(player_id)

    def can_start(self) -> bool:
        return True  # TODO: delete
        return len(self.channels) >= Game.MIN_PLAYERS

    async def start(self):
        if not self.can_start():
            await self.view.print_group(f"Игра отменена. Требуется минимум {Game.MIN_PLAYERS} игроков")
            self.app["events"].unsubscribe_callback(self.group_chat_id)
            for p in self.channels:
                self.app["events"].unsubscribe_callback(p.user_id, self)    
            return
        await self.view.print_group(game_info["description"] + game_info["on_start_tip"])        
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
        self.view.init()
        for p in self.board.players:
            assert type(p) == Player
            p.init(self.view, self)
            self.app["events"].subscribe_callback(p.user_id, self)
        await self.run()

    # TODO: ------------------------------- refactor -------------------

    async def run(self):
        # До старта игры показываем карты игрокам, пишем историю ситуации и ждём, чтобы они прочитали
        assert len(self.board.players) > 0
        p = self.board.next_turn()
        await self.view.show_cards_to_all()
        
        while not self.board.is_end:
            await asyncio.sleep(0)
            p.global_log = []
            # Рисуем стол и очередность в общем чате
            await self.view.show_table_to_all()
            if not await p.phase1():
                continue
            
            await p.phase2_prepare()
            await p.phase2()
            await p.phase2_end()

            next_player = self.board.player_next(p)
            await p.phase3_prepare(next_player)
            await p.phase3(next_player)

            p.global_log = []
            p = self.board.next_turn()
        await self.view.print_group("game ended")
        return
