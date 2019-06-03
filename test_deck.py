import asyncio
import random
from app.game import Game
from app.test_view import TestView
from app.events import EventsQueue
from config import get_config

if __name__ == "__main__":
    random.seed(6)
    game = Game()
    game.group_chat_id = 65536
    game.app = {"events": EventsQueue(), "cfg": get_config()}
    tv = TestView()
    tv.init(game)
    game.set_view(tv)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(game.start())
    except KeyboardInterrupt:
        print("Exiting...")
    # loop.run_until_complete(game.run())
    loop.close()
