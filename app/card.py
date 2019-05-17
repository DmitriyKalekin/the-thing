import types
# from app.player import Player
class IPlayableToTarget:
    def get_targets(self, p: "Player"):
        pass


class IPlayableToPerson(IPlayableToTarget):
    
    def on_played_to_person(self, p: "Player", target: "Player"):
        print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return True
    
    def get_targets(self, p: "Player"):
        if "person_target" not in self.__dict__:
            self.person_target = ["prev", "next"]
        assert type(self.person_target) == list
        
        if p.is_quarantined():
            return []

        candidates = []
        for pt in self.person_target:
            if pt == "self":
                candidates.append(p)
            if pt == "next":
                next_player = self.board.player_next(p)
                if not next_player.is_quarantined():
                    candidates.append(next_player)
            if pt == "prev":
                prev_player = self.board.player_prev(p)
                if not prev_player.is_quarantined():
                    candidates.append(prev_player)
            if pt == "any":
                for any_player in self.board.players:
                    if any_player == p or any_player.is_quarantined():
                        continue
                    candidates.append(any_player)
        return candidates

class IPlayableToSeat(IPlayableToTarget):
    def get_targets(self, p: "Player"):
        pass

class IPlayableToDoor(IPlayableToTarget):
    def get_targets(self, p: "Player"):
        pass

class IDefCardExchange:
    pass

class IDefSeatsSwap:
    pass

class IDefFire:
    pass


class IPanic:
    pass


class Card:
    """
    """
    TYPE_PANIC = "panic"

    # PLAY_PERSON = "on_played_to_person"

    def __init__(self, board, d: dict):
        self.uuid = None
        self.type = None
        self.color = None
        self.name = None 
        self.players = None
        self.images = None
        self.board = board
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

    def is_infection(self):
        return isinstance(self, CardInfection)

    def is_panic(self):
        return self.type == Card.TYPE_PANIC  
    
    def is_evil(self):
        return isinstance(self, CardEvil)

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
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardInfection(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardFlamethrower(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)

    def on_played_to_person(self, p: "Player", target: "Player"):
        print(f"ОГНЕМЁТ!!! {p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return True


class CardBloodTest(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)
    
    def on_played_to_person(self, p: "Player", target: "Player"):
        print(f"ТЕСТ КРОВИ!!! {p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return True


class CardAxe(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)

    def on_played_to_person(self, p: "Player", target: "Player"):
        self.board.break_door(p, target)
        print("Сломана дверь")
        print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name) 
        return True

class CardSuspicion(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardWhiskey(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardPerseverance(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardLookAround(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardChangePlaces(Card, IPlayableToSeat):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardWindUps(Card, IPlayableToSeat):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardTemptation(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)

    def on_played_to_person(self, p: "Player", target: "Player"):
        p._next_player = target
        print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return False


class CardFear(Card, IDefCardExchange):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




class CardNotBadHere(Card, IDefSeatsSwap):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




class CardNoThanks(Card, IDefCardExchange):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




class CardMiss(Card, IDefCardExchange):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




class CardNoBbq(Card, IDefFire):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




class CardQuarantine(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)

    def on_played_to_person(self, p: "Player", target: "Player"):
        target.set_quarantined(True)
        print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return True



class CardDoor(Card, IPlayableToPerson):
    def __init__(self, board, d: dict):
        super().__init__(board, d)

    def on_played_to_person(self, p: "Player", target: "Player"):
        self.board.set_door(p, target)
        print("Установлена дверь")
        print(f"{p.name} сыграл. {self.name} сыгран на игрока", target.name)
        return True        


class CardOldRope(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardOneTwo(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardThreeFour(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardParty(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardGoAway(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardForgetfulness(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardChainReaction(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardFriendship(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardBlindDating(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardOops(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardBetweenUs(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardConfessionTime(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardLovecraft(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)


class CardNecronomicon(Card):
    def __init__(self, board, d: dict):
        super().__init__(board, d)




