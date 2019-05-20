import random
from app.player import Player
# from app.card import Card
from app.misc import chunks
from app.deck_normal import card_deck_struct
from itertools import cycle
import importlib

class Board:
    """
    """
    CARDS_ON_HAND = 4   # Количество карт на руке у игрока

    def __init__(self, list_players: list):
        n = len(list_players)
        assert n >= 4
        self.n = n
        self.players = []  # Индексы - места за столом
        self.doors = []  # Список множеств из двух элементов
        self._cards = self.load_cards(card_deck_struct, n)
        init_hands, self.deck = self.split_deck(self._cards, n)
        for i, hand in enumerate(init_hands):
            self.players.append(Player(hand, self, list_players[i]))
        
        random.shuffle(self.players)
        self.turn = -1  # Чья очередь. Пока ничья
        self.move = 0   # Номер ходя по порядку
        self.turn_sequence = 1  # -1
        self.current_player = self.players[0]

    def is_end(self):
        return self.evil_dead() or self.all_players_infected()
    
    def evil_dead(self):
        for p in self.players:
            if p.is_evil():
                return False
        return True

    def all_players_infected(self):
        for p in self.players:
            if p.is_good():
                return False
        return True

    def get_player(self, uuid):
        for u in self.players:
            if u.uuid == uuid:
                return u

    def kill_player(self, p: Player):
        members = []
        for _ in self.players:
            if _ != p:
                members.append(_)
        self.deck.extend(p.hand)
        self.players = members
        print(f"Игрок {p.name} покинул игру, его карты помещены в колоду")
        


    def get_player_seat(self, p: Player):
        for i, _ in enumerate(self.players):
            if p == _:
                return i
        raise Warning("ERROR: player outside the table")

    def set_door(self, p: Player, target: Player):
        d = {self.get_player_seat(p), self.get_player_seat(target)}
        if d not in self.doors:
            self.doors.append(d)

    def break_door(self, p: Player, target: Player):
        d = {self.get_player_seat(p), self.get_player_seat(target)}
        if d not in self.doors:
            raise Warning("ERROR: no door between players")
        self.doors = list([_ for _ in self.doors if _ != d])

    def is_door(self, p: Player, target: Player):
        d = {self.get_player_seat(p), self.get_player_seat(target)}
        return d in self.doors
               

    async def update_players_hands(self):
        pass
        # for i, p in enumerate(self.players):

    # def current_player(self) -> Player:
    #     """
    #     Возвращает текущего игрока
    #     """
    #     return self.players[self.turn]
    
    def player_before(self):
        if self.turn-1 < 0:
            return self.players[:-1]
        return self.players[self.turn-1]

    def player_after(self):
        if self.turn+1 > len(self.players)-1:
            return self.players[0]
        return self.players[self.turn+1]

    def player_by_uuid(self, uuid):
        return next(p for p in self.players if p.uuid == uuid)

    def player_prev(self, p):
        """
        Возвращает следующего игрока в зависимости от направления очередности
        """
        assert len(self.players) > 0
        if not p:
            return self.players[0]
        iterator = self.players if self.turn_sequence < 0 else reversed(self.players)
        iterator = cycle(iterator)
        for cp in iterator:
            if cp == p:
                return next(iterator)
        return None

    def player_next(self, p):
        """
        Возвращает следующего игрока в зависимости от направления очередности
        """
        assert len(self.players) > 0
        if not p:
            return self.players[0]
        iterator = self.players if self.turn_sequence > 0 else reversed(self.players)
        iterator = cycle(iterator)
        for cp in iterator:
            if cp == p:
                return next(iterator)
        return None  # TODO: игрок может убиться - будет проблема
        # index = self.turn + self.turn_sequence
        # if index > len(self.players)-1:
        #     index = 0
        # if index < 0:
        #     index = len(self.players)-1 
        # return self.players[index]
    
    def next_turn(self):
        """
        Переход хода в зависимости от направления очередности
        """
        # self.turn += self.turn_sequence
        # if self.turn > len(self.players)-1:
        #     self.turn = 0
        # if self.turn < 0:
        #     self.turn = len(self.players)-1 
        if self.current_player:
            self.current_player.global_log = []
        if self.move == 0:
            self.current_player = self.player_next(None)
        else:
            self.current_player = self.player_next(self.current_player)
        self.move += 1
        self.current_player.global_log = []
        return self.current_player
        
    def load_cards(self, card_deck_struct, n):
        """
        Делает и описательной структуры физическую колоду
        и производит валидацию, верно ли заполнена структура
        В конце смотрит, на какое количество игроков сформировать колоду
        """
        module = importlib.import_module("app.card")
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
                
                class_ = getattr(module, c["_class_name"])
                cards.append(class_(self, {
                    "uuid": subcard_index,
                    "players": c["_players"][i],
                    ** {k: v for k, v in c.items() if k not in ["_uuids", "_players", "_class_name", "_proto"]}
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