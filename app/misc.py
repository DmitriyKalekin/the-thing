def chunks(l: list, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]

def list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


def print_trace():
    import traceback
    for line in traceback.format_stack():
        print(line.strip())    


def get_group_memgers():
    from telethon import TelegramClient
    from config import get_config
    cfg = get_config()
    client = TelegramClient('session_name', cfg.API_ID, cfg.API_HASH).start()
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(cfg.API_PHONE_NUMBER)
        me = client.sign_in(cfg.API_PHONE_NUMBER, input('Enter code: '))
        print(me)
    client.send_message('@herr_horror', '1111Server started.\nClient loaded.') 
    members = client.get_participants('TheThingDevTest')
    for m in members:
        # UserStatusOffline
        # UserStatusOnline
        # UserStatuserecently
        print(m.id, m.bot, m.first_name, m.last_name, m.username, m.status.__class__.__name__)        


# def clear(): 
#     from os import system, name
#     if name == 'nt': 
#         _ = system('cls') 
#     else:
#         _ = system('clear')

# class Games:
#     def __init__(self, app):
#         self.app = app
#         self._storage = dict()

#     def get_game(self, chat_id: int) -> "Game":
#         if chat_id < 0:
#             cur_game = self._storage.get(chat_id, None)
#             if not cur_game:
#                 self._storage[chat_id] = Game(chat_id, self.app)
#             return self._storage[chat_id]
#         else:
#             print("Попытка взять игру из индивидуального чата")