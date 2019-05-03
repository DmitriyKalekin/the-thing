import os
from _private_.telegram_key import CFG_TELEGRAM_KEY, CFG_API_ID, CFG_API_HASH, CFG_PHONE_NUMBER

# class Config:
#     TELEGRAM_KEY = CFG_TELEGRAM_KEY
#     URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/'
#     LOCAL_PATH = 'root/tele_tec_bot'
#     # HOST = "0.0.0.0"
#     # PORT     = "443"
#     DEBUG = True
#     # CERT     = f'/{LOCAL_PATH}/_private_/bundle.crt' 
#     # CERT_KEY = f'/{LOCAL_PATH}/_private_/certificate.key' 
#     # CONTEXT = (CERT, CERT_KEY)
    
#     # WH_URL = 'https://eva-bot.ru/'
class Config:
    ENV = os.getenv('ENV')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    TELEGRAM_KEY = CFG_TELEGRAM_KEY
    API_ID  =  CFG_API_ID
    API_HASH = CFG_API_HASH
    API_PHONE_NUMBER = CFG_PHONE_NUMBER
    URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/'
    WH_URL = f'https://eva-bot.ru:{PORT}/'    


# class LocalConfig:
#     TELEGRAM_KEY = CFG_TELEGRAM_KEY
#     URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/'
#     HOST = "127.0.0.1"
#     PORT = 5000
#     WH_URL = f"https://127.0.0.1:{PORT}/"

# class MasterConfig:
#     TELEGRAM_KEY = CFG_TELEGRAM_KEY
#     URL = f'https://api.telegram.org/bot{TELEGRAM_KEY}/'
#     HOST = "0.0.0.0"
#     PORT = 8443
#     WH_URL = f'https://eva-bot.ru:{PORT}/'


def get_config():
    return Config()
     
