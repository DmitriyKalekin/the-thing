import types


class Card:
    """
    """
    TYPE_PANIC = "panic"

    PLAY_PERSON = "on_played_to_person"

    def __init__(self, d: dict):
        self.uuid = None
        self.type = None
        self.color = None
        self.name = None 
        self.players = None
        self.images = None
        # self.message_id = None

        for key in d:
            if key[1] == "_":
                continue

            # assert key in self.__dict__ or key[:3] == "on_", f"{key} not in keys" # 
            # if key in self.__dict__:
            
            if key[:3] == "on_":
                setattr(self, key, types.MethodType(d[key], self))
            else:
                setattr(self, key, d[key]) 

    def __repr__(self):
        return "<Card: %s, uuid=%s>" % (self.name, self.uuid)  # self.__dict__            

    def is_def_exchange(self):
        return False

    def is_def_flamethrower(self):
        return False

    def is_def_change_place(self):
        return False

    def is_infection(self):
        return type(self) == CardInfection  

    def is_panic(self):
        return self.type == Card.TYPE_PANIC  
    
    def is_evil(self):
        return type(self) == CardEvil 

    def is_playable(self):
        return not self.is_infection() and not self.is_evil()

    def on_taken(self, p):
        """
        Срабатывает при вытягивании из колоды
        """
        assert p.__class__.__name__ == "Player"
        pass

    def on_accepted(self, p, sender):
        """
        Срабатывает при получении карты от другого игрока
        Перекрывается в файле со структурой колоды
        """
        assert p.__class__.__name__ == "Player"
        assert p.__class__.__name__ == "Player"
        pass




class CardEvil(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardInfection(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardFlamethrower(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardBloodTest(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardAxe(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardSuspicion(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardWhiskey(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardPerseverance(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardLookAround(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardChangePlaces(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardWindUps(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardTemptation(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardFear(Card):
    def __init__(self, d: dict):
        super().__init__(d)

    def is_def_exchange(self):
        return True


class CardNotBadHere(Card):
    def __init__(self, d: dict):
        super().__init__(d)

    def is_def_change_place(self):
        return True


class CardNoThanks(Card):
    def __init__(self, d: dict):
        super().__init__(d)

    def is_def_exchange(self):
        return True


class CardMiss(Card):
    def __init__(self, d: dict):
        super().__init__(d)

    def is_def_exchange(self):
        return True


class CardNoBbq(Card):
    def __init__(self, d: dict):
        super().__init__(d)

    def is_def_flamethrower(self):
        return True


class CardQuarantine(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardDoor(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardOldRope(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardOneTwo(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardThreeFour(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardParty(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardGoAway(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardForgetfulness(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardChainReaction(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardFriendship(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardBlindDating(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardOops(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardBetweenUs(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardConfessionTime(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardLovecraft(Card):
    def __init__(self, d: dict):
        super().__init__(d)


class CardNecronomicon(Card):
    def __init__(self, d: dict):
        super().__init__(d)




