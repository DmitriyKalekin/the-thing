def chunks(l: list, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


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
        # UserStatusRecently
        print(m.id, m.bot, m.first_name, m.last_name, m.username, m.status.__class__.__name__)        