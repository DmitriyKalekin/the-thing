from app.card import Card, CardInfection, CardEvil, IPlayableToPerson, IDefCardExchange
import asyncio
import uuid
import traceback
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
        self.uuid = str(uuid.uuid4())
        self.hand = hand
        self.board = board
        self.game = None
        self.side = Player.GOOD
        self.update_player_side()
        self.avatar = "😺"
        self.set_avatar()
        self.view = None
        self._quarantined = False
        self._quarantine_counter = 0
        self._target_player = None

    def __repr__(self):
        return "<Player: %s, user_id=%s, uuid=%s>" % (self.user_fullname, self.user_id, self.uuid)  # self.__dict__           

    def init(self, view, game):
        self.view = view
        self.game = game

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

    async def phase1(self) -> bool:
        """
        Фаза взятия карты и игры паники
        Возвращает необходимость продолжать код
        """
        # p.global_log = "тянет карту с колоды..."
        # await self.show_table_to_all()
        # await self.show_log_to_all(f"Фаза 1. {p.user_fullname} тянет карту с колоды")
        print(f"ФАЗА 1. Игрок {self.name}")
        card = self.pull_deck()
        assert isinstance(card, Card)
        if card.is_panic():
            self.play_panic(card)
            self.board.deck.append(card)  # карта паники ушла в колоду
            return False
        else:
            await self.take_on_hand(card)
            return True   
        return True



    async def phasedef(self, card: Card, attacker: "Player") -> bool:
        """
        Фаза защиты от игры с руки
        True - если получилось защититься
        False - не получилось
        """
        candidates = self.get_possible_def(card)
        if not candidates:
            return False
        
        # ----------------- TODO: refactor --------------------
        print("Вошли в подготовку")
        self.local_log.append(f"❗️ Защититесь 🛡 или разрешите ☠️ сыграть против вас карту {card.name}")
        self.global_log.append(f"⏳ Принимает решение ...")
        await asyncio.wait([
            self.view.show_def_options(self, candidates),
            self.view.show_table_to_all()
        ])


        cmd, card_uuid = await self.game.input(self)
        assert cmd in ["phasedef:def_card", "phasedef:allow"]
        if cmd == "phasedef:allow":
            print(f"{self.name} разрешает сыграть против себя карту")
            self.local_log.append(f"☠️ разрешил сыграть на себя карту {card.name}")
            self.global_log.append(f"☠️ Разрешил сыграть на себя карту {card.name}")
            # await self.view.show_table_to_all()
            return False

        # Защита против сыгранного
        card_def = self.pop_card_by_uuid(int(card_uuid))  # выбранная карта
        self.local_log.append(f"🛡 защитился от карты {card.name}, сыграв {card_def.name}")
        self.global_log.append(f"🛡 Защитился от карты {card.name}, сыграв {card_def.name}")
        print("Добавлено в локальный и глобальный лог")
        assert isinstance(card_def, Card)
        if cmd == "phasedef:def_card":
            self.play_card(card_def, target=None)
            self.board.deck.append(card_def)

            card_deck = self.pull_deck()
            while card_deck.is_panic():
                self.board.deck.append(card_deck)
                card_deck = self.pull_deck()
            await self.take_on_hand(card_deck, silent=True)
        # await self.view.show_table_to_all()
        return True


    async def phase2_prepare(self):
        self.local_log.append(f"❗️ Сыграйте ▶️ или сбросьте 🗑 карту...")
        self.global_log.append(f"🃏 Играет или сбрасывает...")
        await asyncio.wait([
            self.view.show_play_drop_options(self),
            # self.view.show_table_to_all()
        ])

    async def end_phase(self):
        await asyncio.wait([
            self.view.show_cards(self),
            # self.view.show_table_to_all()
        ])


    async def phase2(self):
        """
        Фаза сброса или игры карты с руки
        """
        
        target = None
        card = None
        cmd, card_uuid = await self.game.input(self)
        assert cmd in ["phase2:play_card", "phase2:drop_card"]
        card = self.pop_card_by_uuid(int(card_uuid))  # выбранная карта
        assert isinstance(card, Card)
        if cmd == "phase2:play_card":
            if isinstance(card, IPlayableToPerson):
                candidates = card.get_targets(self)
                if len(candidates) > 1:
                    await self.view.show_player_target(self, candidates)
                    cmd, p_uuid = await self.game.input(self)
                    assert cmd == "phase2:play_card/player"
                    target = self.board.player_by_uuid(p_uuid)
                elif len(candidates) == 1:
                    target = candidates[0]
                else:
                    print("ERROR: len(candidates) == 0")
                    print(candidates)
                    return

                self.play_card(card, target=target)
                # await self.view.show_table_to_all()                    



            else:
                self.play_card(card, target=None)
            self.board.deck.append(card)
        else:
            assert cmd == "phase2:drop_card"
            self.drop_card(card)

        await self.end_phase()

        return target, card

    async def phase3_prepare(self, next_player: "Player"):
        self.local_log.append(f"❗️ Передайте карту для *{next_player.user_fullname}*")
        self.global_log.append(f"⏳ Передаёт карту для {next_player.user_fullname}")

        next_player.local_log.append(f"❗️ Передайте карту для *{self.user_fullname}*, либо защититесь 🛡 от обмена.")
        next_player.global_log.append(f"⏳ Передаёт карту для {self.user_fullname}")

        await asyncio.wait([
            self.view.show_give_options(self, next_player),
            self.view.show_give_options(next_player, self, can_def=True),
            # self.view.show_table_to_all()
        ])

    async def phase3(self, next_player: "Player"):
        exchangers = await asyncio.gather(*[
            self.proccess_exchange(next_player),
            next_player.proccess_exchange(self)
        ])
        p1, card1 = exchangers[0]
        p2, card2 = exchangers[1]
        assert type(p1) == Player
        assert type(p2) == Player
        assert isinstance(card1, Card)
        assert isinstance(card2, Card)
        await asyncio.wait([
            p1.take_on_hand(card2, sender=p2),
            p2.take_on_hand(card1, sender=p1)
        ])
        return

    async def proccess_exchange(self, next_player: "Player"):
        cmd, card_uuid = await self.game.input(self)
        # BUG: assertion error here
        assert cmd in ["phase3:give_card", "phase3:block_exchange_card"]
        my_card = self.pop_card_by_uuid(int(card_uuid))
        assert isinstance(my_card, Card)

        if cmd == "phase3:give_card":
            self.local_log.append(f"🎁 отдана `{my_card.name}` для *{next_player.user_fullname}*")
            self.global_log.append(f"♣️ Отдал карту для {next_player.user_fullname}")
        else:
            assert cmd == "phase3:block_exchange_card"
            self.local_log.append(f"🛡 сыграна защита `{my_card.name}` от *{next_player.user_fullname}*")        
            self.global_log.append(f"🛡 Защитился `{my_card.name}` от обмена с {next_player.user_fullname}")
        return self, my_card

    def update_player_side(self):
        for c in self.hand:
            if c.is_evil():
                self.side = Player.EVIL

    def get_cards_names(self):
        return [c.name for c in self.hand]

    def get_possible_play(self):
        result = []
        for c in self.hand:
            if c.is_playable() and type(c) not in [type(_) for _ in result]:
                if isinstance(c, IPlayableToPerson):
                    candidates = c.get_targets(self)
                    if len(candidates) > 0:
                        result.append(c)
        return result

    def get_possible_def(self, card: Card):
        ret = []
        print("Защита от карты:", card.__class__.__name__)
        for c in self.hand:
            print(c.__dict__.get("def_play", []))
            if card.__class__.__name__ in c.__dict__.get("def_play", []):
                print("Защита найдена")
                ret.append(c)
        print("Возможно сыграть в ответ:", ret)
        return ret
        



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

    def is_quarantined(self):
        return self._quarantined

    def set_quarantined(self, v: bool):
        print(f"{self.name} статус карантина: ", v)
        self._quarantined = v
        self._quarantine_counter = 3 if v else 0


    def get_possible_drop(self):
        result = []
        for c in self.hand:
            # именно одну карту заражения нельзя скидывать - т.е. одна всегда пропустится и останется на руке
            if self.is_infected() and self.cnt_infection() == 1 and c.is_infection():
                continue
            if type(c) not in [*[type(_) for _ in result], CardEvil]:
                result.append(c)
        # Запрещаем скидывать нормальную карту
        # чтобы не допустить случая, когда все карты на руке - заражение
        if not self.is_evil() and len(self.hand) == 5 and self.cnt_infection() == 4:
            return [next(c for c in result if c.is_infection())]
        return result        

    def get_possible_give(self, receiver: "Player"):
        wrong_cards = [CardEvil]
        if self.is_good():
            wrong_cards.append(CardInfection)
        if self.is_infected() and not receiver.is_evil():
            wrong_cards.append(CardInfection)
        if self.is_infected() and receiver.is_evil() and self.cnt_infection() == 1:
            wrong_cards.append(CardInfection)

        result = []
        for c in self.hand:
            if type(c) not in [*[type(_) for _ in result], *wrong_cards]:
                result.append(c)               
        return result

    def get_possible_block_exchange(self):
        result = []
        for c in self.hand:
            if type(c) not in [type(_) for _ in result] and isinstance(c, IDefCardExchange):
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
                #         assert isinstance(card, Card)
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

    async def take_on_hand(self, card, sender=None, silent=False):
        self.hand.append(card)
        if not sender:
            self.local_log.append(f"🎲 событие `{card.name}` c колоды")
            if not silent:
                self.global_log.append(f"🎲 Вытянул событие из колоды")        

        if sender and sender.is_evil() and card.is_infection() and not self.is_evil():
            self.become_infected()

        if sender:
            self.local_log.append(f"🤲 получена `{card.name}` от *{sender.user_fullname}*")
            sender.global_log.append(f"👌🏻 Передал карту {self.user_fullname}")
        # for j, s in enumerate(self.hand_slots):
        #     if not s["card"]:
        #         self.hand_slots[j]["card"] = card 
        print(f"{self.name}: Карта добавлена на руку:", card.name)  
        await self.view.show_cards(self)

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
        self.local_log.append(f"▶️ сыграна `{card.name}`" + f" против {target.name}" if target else "")
        self.global_log.append(f"▶️ Сыграл карту `{card.name}`" + f" против {target.name}" if target else "")
        print(f"{self.name} сыграл карту {card.name}")
        
        return True

    def play_panic(self, card: Card):
        self.local_log.append(f"🔥 паника `{card.name}` с колоды, ход завершён.")
        self.global_log.append(f"🔥 Вытянул панику `{card.name}` с колоды. Ход завершён.")        
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
        self.local_log.append(f"🗑 сброшена `{card.name}`")   
        self.global_log.append(f"🗑 Сбросил карту")
        self.board.deck.append(card)
        print(f"Карта {card.name} помещена в колоду")