import asyncio
from app.game import Game
from app.telebot import Message, Callback


class EventsQueue:
    def __init__(self):
        self.events = []
        self.__observers = []
        self.__callbacks = dict()

    def set_application(self, app):
        self.app = app 

    def register_observer(self, observer):
        self.__observers.append(observer)

    def subscribe_callback(self, chat_id: int, handler: Game):
        self.__callbacks[chat_id] = handler

    def unsubscribe_callback(self, chat_id: int):
        del self.__callbacks[chat_id]

    async def notify_observers(self, msg: Message):
        for observer in self.__observers:
            print("observer:", observer)
            await asyncio.sleep(0)
            await observer.update(msg)
        return
    
    async def notify_callbacks(self, callback: Callback):
        await asyncio.sleep(0)
        key_id = callback.chat_id
        game = self.__callbacks.get(key_id, None)
        print(self.__callbacks)
        if game:
            assert type(game) == Game
            await game.update_callback(callback)
        else:
            print("Игра не найдена для канала", key_id)
        return

    async def listen(self):
        """
        """
        while True:
            while len(self.events) > 0:
                e = self.events.pop(0)
                await self.fire_event(e)
            await asyncio.sleep(1)
        return


# class EventBase(self):
#     def __init__(self, **kwargs):
#         pass

# class EventCallback(EventBase):
#     def __init__(self, **kwargs):
#         pass

# class EventCommand(EventBase)
#     def __init__(self, **kwargs):
#         pass


# class EventFactory:
#     def __init__(self):
#         pass
    
#     def create_Command(r: dict):
#         pass
