import random
from game.player import Player
from game.card import Card
from game.misc import chunks
from decks.deck_normal import card_deck_struct
import asyncio


# def clear(): 
#     from os import system, name
#     if name == 'nt': 
#         _ = system('cls') 
#     else:
#         _ = system('clear')

class Games:
    def __init__(self, app):
        self.app = app
        self._storage = dict()

    def get_game(self, chat_id: int) -> "Game":
        if chat_id < 0:
            cur_game = self._storage.get(chat_id, None)
            if not cur_game:
                self._storage[chat_id] = Game(chat_id, self.app)
            return self._storage[chat_id]
        else:
            print("Попытка взять игру из индивидуального чата")
            


class Game:
    MIN_PLAYERS = 4
    STATUS_PENDING = "pending"
    STATUS_LAUNCHED = "launched"
    STATUS_CANCELED = "canceled"

    def __init__(self, chat_id, app):
        self.chat_id = chat_id
        self.players = []
        self.status = Game.STATUS_PENDING
        self.board = None
        self.app = app
        self.events_invoker = app["events_invoker"]

    def add_player(self, player_id):
        if player_id not in self.players:
            self.players.append(player_id)

    def can_start(self) -> bool:
        return len(self.players) >= Game.MIN_PLAYERS

    def create_board(self):
        mock_players = self.players
        # TODO: delete this mock

        mock_players = [
            {
                "chat_id": -272083086,
                "usr_id": 435627225,
                "usr_fullname": "Дмитрий Калекин",
                "usr_alert": "@herr_horror Дмитрий"
            },
            {
                "chat_id": -272083086,
                "usr_id": 435627225,
                "usr_fullname": "Dmitriy Zaytsev",
                "usr_alert": "@1"
            },
            {
                "chat_id": -272083086,
                "usr_id": 435627225,
                "usr_fullname": "Zag",
                "usr_alert": "@2"
            },
            {
                "chat_id": -272083086,
                "usr_id": 435627225,
                "usr_fullname": "Александр Грицай",
                "usr_alert": "@3"
            }                                     
        ]
        self.board = Board(mock_players)

    async def phase1(self, p: Player) -> bool:
        """
        Фаза взятия карты и игры паники
        Возвращает необходимость продолжать код
        """
        await self.events_invoker.print(self.chat_id, f"Фаза 1. {p.usr_fullname} тянет карту с колоды")
        card = p.pull_deck()
        if not card.is_panic():
            p.take_on_hand(card)
            await self.events_invoker.print(self.chat_id, f"Добавлена на руку карта события: {card.name}. Теперь нужно сыграть карту или сбросить.")
            await self.events_invoker.show_cards(p)
            return True
        else:
            await self.events_invoker.print(self.chat_id, f"Вытянута карта паники {card.name}. Все забегали")
            p.play_panic(card)
            self.board.deck.append(card)  # карта паники ушла в колоду
            return False
        return True

    async def phase2(self, p: Player):
        """
        Фаза сброса или игры карты с руки
        """
        # Обновили карты на руке игрока и ждём от него хода
        await self.events_invoker.show_cards(p)
        decision = await self.events_invoker.show_play_drop_options(p)

        cmd = None
        while cmd not in ["phase2:play_card", "phase2:drop_card"]:
            cmd = await self.events_invoker.input(self.chat_id, "Фаза 2. Играйте или скиньте карту") 
        
        if cmd == "p":
            possible = p.get_possible_play()
        elif cmd == "d":
            possible = p.get_possible_drop()
        
        indices = []
        for i, c in enumerate(p.hand):
            if c.uuid not in possible:
                continue
            await self.events_invoker.print(self.chat_id, f"{i} {c.name}")
            indices.append(str(i))
        card_index = None
        while card_index not in indices:
            card_index = await self.events_invoker.input(p.usr_id, f"Какую карту? {indices} >>> ")

        card = p.hand.pop(int(card_index))  # выбранная карта
        if cmd == "p":
            p.play_card(card, target=None)
        p.drop_card(card)  # в любом случае в колоду
        return

    async def phase3(self, p: Player):
        await self.events_invoker.print(self.chat_id, "Фаза 3. Обмен картами со следующим игроком")
        next_player = self.board.player_next()
        possible = p.get_possible_give(next_player)
        indices = []
        for i, c in enumerate(p.hand):
            if c.uuid not in possible:
                continue
            await self.events_invoker.print(f"{i} {c.name}")
            indices.append(str(i))
        card_index = None
        while card_index not in indices:
            card_index = await self.events_invoker.input(p.usr_id, f"Какую карту даём ему? {indices} >>> ")
        my_card = p.hand.pop(int(card_index))  # выбранная карта      
        p.swap_cards(my_card, next_player)
        return

    async def run(self):
        # До старта игры показываем карты игрокам, пишем историю ситуации и ждём, чтобы они прочитали
        await self.events_invoker.update_players_hands(self.board.players)
        await self.events_invoker.print(self.chat_id, "История игры: как вы сюда попали такова...\nМного текста...")
        await asyncio.sleep(5)

        while not self.board.is_end:
            self.board.next_turn()
            p = self.board.current_player()
            # Рисуем стол и очередность в общем чате
            await self.events_invoker.print(self.chat_id, self.board.print_hands())
            # Тянем карту: либо паника и переход хода, либо фаза сыграть карту с руки
            if not await self.phase1(p):
                await self.events_invoker.print(self.chat_id, f"Ход переходит к следующему игроку")
                continue
            await self.phase2(p)
            await self.phase3(p)
        await self.events_invoker.print("game ended")
        return


class Board:
    """
    """
    CARDS_ON_HAND = 4   # Количество карт на руке у игрока

    def __init__(self, list_players: list):
        n = len(list_players)
        assert n >= 4
        self.n = n
        self.players = []
        self._cards = self.load_cards(card_deck_struct, n)
        init_hands, self.deck = self.split_deck(self._cards, n)
        for i, hand in enumerate(init_hands):
            self.players.append(Player(hand, self, list_players[i]))
        
        random.shuffle(self.players)
        self.turn = -1  # Чья очередь. Пока ничья
        self.move = 0   # Номер ходя по порядку
        self.is_end = False
        self.turn_sequence = 1  # -1

    def get_player(self, uuid):
        for u in self.players:
            if u.uuid == uuid:
                return u

    async def update_players_hands(self):
        pass
        # for i, p in enumerate(self.players):

    def print_hands(self):
        output = f"Ход {self.move}, ходит {self.current_player().usr_fullname} \r\n"
        for i, p in enumerate(self.players):
            turn = "✔️" if i == self.turn else ""
            # output += "```"
            output += f"{p.avatar} {p.name}({len(p.hand)}) {turn}\r\n" 
            # output += "```"            
            for o in p.get_cards_names():
                if o == "Заражение":
                    output += "`[`🤢`" + o + "]`; "                                    
                if o == "Нечто":
                    output += "`[`🍄`" + o + "]`; "
                else:
                    output += "`[" + o + "]`; "
            output += "\r\n"
        return output

    def current_player(self) -> Player:
        """
        Возвращает текущего игрока
        """
        return self.players[self.turn]
    
    def player_before(self):
        if self.turn-1 < 0:
            return self.players[:-1]
        return self.players[self.turn-1]

    def player_after(self):
        if self.turn+1 > len(self.players)-1:
            return self.players[0]
        return self.players[self.turn+1]
    
    def player_next(self):
        """
        Возвращает следующего игрока в зависимости от направления очередности
        """
        index = self.turn + self.turn_sequence
        if index > len(self.players)-1:
            index = 0
        if index < 0:
            index = len(self.players)-1 
        return self.players[index]
    
    def next_turn(self):
        """
        Переход хода в зависимости от направления очередности
        """
        self.turn += self.turn_sequence
        if self.turn > len(self.players)-1:
            self.turn = 0
        if self.turn < 0:
            self.turn = len(self.players)-1        
        self.move += 1
        
    def load_cards(self, card_deck_struct, n):
        """
        Делает и описательной структуры физическую колоду
        и производит валидацию, верно ли заполнена структура
        В конце смотрит, на какое количество игроков сформировать колоду
        """
        cards = []
        for c in card_deck_struct:
            if not isinstance(c["_uuids"], list):
                raise TypeError("Type error " + c["name"])
            if len(c["_uuids"]) == 0:
                raise IndexError("Index error: " + c["name"])
            if len(c["_uuids"]) != len(c["_players"]):
                raise IndexError("Index error: len_index!=len " + c["name"])
            index = c["_uuids"][0]
            for i, subcard_index in enumerate(c["_uuids"]):
                if i+index != subcard_index:
                    raise IndexError("Skipped index: " + c["name"])
                # Карта не предусмотрена на это количество игроков
                if c["_players"][i] > n:
                    continue    
                cards.append(Card({
                    "uuid": subcard_index,
                    "players": c["_players"][i],
                    ** {k: v for k, v in c.items() if k not in ["_uuids", "_players"]}
                }))
        return cards

    def split_deck(self, cards, n):
        """
        Получаем карты для стартовых рук N игроков и остальную кучу
        Карту НЕЧТО кладёв в стартовые руки
        Далее нужно дополнить N*4-1 карт событий, без заражения (удаляем панику и заражение)
        Разделяем на две кучи. Формируем стартовую руку и оставшееся смешиваем.
        """
        assert n >= 4
        start_hands = [cards.pop(0)]  # The thing card
        infection_panic = []
        normal_cards = []
        for c in cards:
            if c.is_panic() or c.is_infection():
                infection_panic.append(c)
            else:
                normal_cards.append(c)
        random.shuffle(infection_panic)  # Куча с паникой и заражением
        random.shuffle(normal_cards)    # куча событий
        start_hands.extend(normal_cards[:Board.CARDS_ON_HAND*n-1])    # отбираем еще N*4-1 карт для рук (НЕЧТО уже там лежит)
        del normal_cards[:Board.CARDS_ON_HAND*n-1]    # удаляем из колоды - они ушли для рук
        random.shuffle(start_hands)         # тасовка карт для рук
        second_heap = list([*normal_cards, *infection_panic])   # Оставшаяся колода: из карт паники, заражения и остатка нормальных
        random.shuffle(second_heap)     # тасуем кучу
        return chunks(start_hands, Board.CARDS_ON_HAND), second_heap 

# def init_hands(self):
#     start_deck = set_card_deck(card_deck_struct, 4)
#     print(len(start_deck))
#     hands, newdeck = deal_start_cards(start_deck, 4)
#     print(len(hands), len(newdeck))
#     pprint(hands)    