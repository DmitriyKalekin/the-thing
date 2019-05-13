from app.card import Card
# import inspect
# from board import Board
# import random
# from emoji import emojize


class Player:
    """
    """

    # Player side CONSTS
    GOOD = 0
    EVIL = 1
    BAD = 2   

    def __init__(self, hand, board, player_info: dict):
        self.title_message_id = None
        self.table_message_id = None
        self.panel_message_id = None
        self.hand_slots = []
        self.log_message_id = None
        self.global_log = []
        self.local_log = []

        self.user_id = player_info["user_id"]
        self.group_chat_id = player_info["group_chat_id"]
        self.name = player_info["user_fullname"]
        self.user_fullname = player_info["user_fullname"]
        self.user_alert = player_info["user_alert"] 
        self.uuid = str(player_info["user_id"]) + str(player_info["group_chat_id"]) + self.user_alert
        self.hand = hand
        self.board = board
        self.side = Player.GOOD
        self.update_player_side()
        self.avatar = "😺"
        self.set_avatar()

    def __repr__(self):
        return "<Player: %s, user_id=%s, uuid=%s>" % (self.user_fullname, self.user_id, self.uuid)  # self.__dict__           

    def set_avatar(self):
        avatars = {
            "Yulia Reznikova": "👩",
            "Джамшид Джураев": "👱️",
            "Anton Mozgovoy": "👨",
            "Tanya Tanya": "👩",
            "Марсель Гиззатов": "👨",
            "Sergey Saltovskiy": "👨",
            "Zair Ognev": "👨",
            "Olga Deribo": "👩", 
            "Дмитрий Калекин": "👨",
            "Igor": "👨",
            "Антон Макарочкин": "👨",
            "Sergey Evseenko": "👨",
            "Zag": "👨",
            "Антон Артюков": "👨",
            "Александр Грицай": "👶",
            "Dmitriy Zaytsev": "👨"
        }
        ava = avatars.get(self.user_fullname, "😺")
        if self.side == Player.EVIL:
            ava = "👾"
        self.avatar = ava
        return
        
    def update_player_side(self):
        for c in self.hand:
            if c.is_evil():
                self.side = Player.EVIL

    def get_cards_names(self):
        return [c.name for c in self.hand]

    def get_possible_play(self):
        result = []
        for c in self.hand:
            if c.is_playable() and c.role not in [_.role for _ in result]:
                result.append(c)
        return result

    def cnt_infection(self):
        cnt = 0
        for c in self.hand:
            if c.is_infection():
                cnt += 1
        return cnt

    def is_fully_infected(self):
        kill_em = True
        for c in self.hand:
            if not c.is_infection():
                kill_em = False
                break
        return kill_em

    def get_possible_drop(self):
        result = []
        print("============ анализирую дроп ........")
        print(f"{self.name}:", self.is_infected())
        for c in self.hand:
            print("Текущая карта:", c.name)
            # именно одну карту заражения нельзя скидывать - т.е. одна всегда пропустится и останется на руке
            if self.is_infected() and self.cnt_infection() == 1 and c.is_infection():
                print("Заражен, количество заражений = 1, и карта заражения")
                continue
            if c.role not in [*[_.role for _ in result], Card.ROLE_EVIL]:
                result.append(c)
        # Запрещаем скидывать нормальную карту
        # чтобы не допустить случая, когда все карты на руке - заражение
        if not self.is_evil() and len(self.hand) == 5 and self.cnt_infection() == 4:
            return [next(c for c in result if c.is_infection())]
        return result        

    def get_possible_give(self, receiver: "Player"):
        wrong_cards = [Card.ROLE_EVIL]
        if self.is_good():
            wrong_cards.append(Card.ROLE_INFECTION)
        if self.is_infected() and not receiver.is_evil():
            wrong_cards.append(Card.ROLE_INFECTION)
        if self.is_infected() and receiver.is_evil() and self.cnt_infection() == 1:
            wrong_cards.append(Card.ROLE_INFECTION)

        result = []
        for c in self.hand:
            if c.role not in [*[_.role for _ in result], *wrong_cards]:
                result.append(c)               
        return result

    def get_possible_block_exchange(self):
        result = []
        for c in self.hand:
            if c.role not in [_.role for _ in result] and c.is_def_exchange():
                result.append(c)               
        return result

    def search_card_index(self, uuid):
        for i, c in enumerate(self.hand):
            if c.uuid == uuid:
                return i
        # raise Warning(f"Card with index {uuid} not found in hand of {self.name}")
        return None

    def get_card_by_uuid(self, uuid):
        for i, c in enumerate(self.hand):
            if c.uuid == uuid:
                return c
        return None

    def pop_card_by_uuid(self, uuid):
        for i, c in enumerate(self.hand):
            if c.uuid == uuid:
                # for j, s in enumerate(self.hand_slots):
                #     if s["card"] and s["card"].uuid == c.uuid:
                #         assert type(s["card"]) == Card
                #         self.hand_slots[j]["card"] = None
                return self.hand.pop(i)
        return None        

    def is_good(self):
        return self.side == Player.GOOD

    def is_evil(self):
        return self.side == Player.EVIL

    def is_infected(self):
        return self.side == Player.BAD 

    def become_infected(self):
        print(f"{self.name} заразился")
        self.side = Player.BAD       

    def become_evil(self):
        self.side = Player.EVIL

    def pull_deck(self) -> Card:
        return self.board.deck.pop(0)   

    def take_on_hand(self, card, sender=None):
        self.hand.append(card)

        if sender and sender.is_evil() and card.role == Card.ROLE_INFECTION and not self.is_evil():
            self.become_infected()
        # for j, s in enumerate(self.hand_slots):
        #     if not s["card"]:
        #         self.hand_slots[j]["card"] = card 
        print("Карта добавлена на руку:", card.name)  

    def accept_card(self, card: Card, sender: "Player"):
        self.hand.append(card)
        card.on_accepted(self, sender)
        return

    def print_log(self, msg, last=False):
        pass

    def play_card(self, card: Card, target=None):
        """
        Если цели нет - просто играется карта
        Если цель игрок - играется на него
        """
        assert target is None or target.__class__.__name__ == "Player"
        print(f"Вы сыграли карту {card.name}")

    def play_panic(self, card: Card):
        print("Автоматом играем карту паники:", card.name)

    def choose_card(self, reason):
        pass

    # def swap_cards(self, card: Card, receiver: "Player"):
    #     # Люди не могут передавать заражение
    #     # assert not (sender.side == Player.GOOD and card_sender.role == Card.ROLE_INFECTION)
    #     # assert not (receiver.side == Player.GOOD and card_receiver.role == Card.ROLE_INFECTION)
    #     # # Зараженный не может передавать человеку или зараженному (только Нечто может)
    #     # assert not (sender.side == Player.BAD and card_sender.role == Card.ROLE_INFECTION and receiver.side in [Player.GOOD, Player.BAD])
    #     # assert not (receiver.side == Player.BAD and card_receiver.role == Card.ROLE_INFECTION and sender.side in [Player.GOOD, Player.BAD])

    #     # if sender.side==Player.EVIL and card_sender.role == Card.ROLE_INFECTION:
    #     #     receiver.side = Player.BAD
    #     #     print(f"Игрок {receiver.name} заразился")

    #     # if receiver.side==Player.EVIL and card_receiver.role == Card.ROLE_INFECTION:
    #     #     sender.side = Player.BAD
    #     #     print(f"Игрок {sender.name} заразился")  

    #     # sender.hand.append(card_receiver)
    #     # receiver.hand.append(card_sender) 
    #     his_possible = receiver.get_possible_give(self)
    #     his_choice_uuid = random.choice(his_possible)
    #     his_card = receiver.hand.pop(receiver.search_card_index(his_choice_uuid))

    #     self.accept_card(his_card, receiver)
    #     receiver.accept_card(card, self)        
    #     print(f"Вы дали карту: {card.name}, а получили {his_card.name}")

    def drop_card(self, card: Card):
        self.board.deck.append(card)
        print(f"Карта {card.name} помещена в колоду")