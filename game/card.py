import types


class Card:
    """
    """
    TYPE_PANIC = "panic"
    ROLE_INFECTION = "infection"
    ROLE_EVIL = "the-thing"

    def __init__(self, d: dict):
        self.uuid = None
        self.role = None
        self.type = None
        self.color = None
        self.name = None 
        self.players = None
        self.images = None
        self.message_id = None

        for key in d:
            # assert key in self.__dict__ or key[:3] == "on_", f"{key} not in keys" # 
            if key in self.__dict__:
                setattr(self, key, d[key]) 
            elif key[:3] == "on_":
                setattr(self, key, types.MethodType(d[key], self))

    def __repr__(self):
        return "<Card: %s, uuid=%s>" % (self.name, self.uuid)  # self.__dict__            

    def is_infection(self):
        return self.role == Card.ROLE_INFECTION

    def is_panic(self):
        return self.type == Card.TYPE_PANIC
    
    def is_evil(self):
        return self.role == Card.ROLE_EVIL  

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



