import configparser
import os


absolute_path = os.path.dirname(os.path.abspath(__file__))
config = configparser.RawConfigParser()
config.read(os.path.join(absolute_path, 'config.ini'), encoding='utf-8-sig')

BUILD = 'local'
# BUILD = 'prod'

if BUILD == 'local':
    CONFIG_DB = 'db_test'
    CONFIG_KASSA = 'kassa'
else:
    CONFIG_DB = 'db'
    CONFIG_KASSA = 'kassa'

LOGS_URL = 'logs'

DB_NAME = config.get(CONFIG_DB, 'NAME')

DB_USER = config.get(CONFIG_DB, 'USER')

DB_HOST = config.get(CONFIG_DB, 'HOST')

DB_PORT = config.get(CONFIG_DB, 'PORT')

DB_PASSWORD = config.get(CONFIG_DB, 'PASSWORD')

GET_PAYMENTS = config.get('variables', 'GET_PAYMENTS_FUNC')

LANGUAGE = config.get('variables', 'LANGUAGE')

SERVICE_ID = int(config.get('variables', 'SERVICE_ID'))

YOOKASSA_ACCOUNT_ID = config.get(CONFIG_KASSA, 'YOOKASSA_ACCOUNT_ID')

YOOKASSA_SECRET_KEY = config.get(CONFIG_KASSA, 'YOOKASSA_SECRET_KEY')

TINKOFF_TERMINAL_KEY = config.get(CONFIG_KASSA, 'TINKOFF_TERMINAL_KEY')

TINKOFF_KASSA_URL = config.get(CONFIG_KASSA, 'TINKOFF_KASSA_URL')

TINKOFF_PASSWORD = config.get(CONFIG_KASSA, 'TINKOFF_PASSWORD')




# NAME_URLS = [
#     "https://auth.flatinn.ru/static/names.txt",
#     "https://guests.flatinn.ru/static/general/names.txt"
# ]
#
# START_LANG = config.get('variables', 'START_LANG')
#
# END_LANG = config.get('variables', 'END_LANG')
#
# END_LANGS = [
#     'fr',
#     'sr',
#     'ar',
#     'az',
#     'ka'
# ]
#
# GET_NAMES = config.get('variables', 'GET_NAMES_FUNC')
#
# UPDATE_NAMES = config.get('variables', 'UPDATE_NAMES_FUNC')
#
# USER_ID = int(config.get('variables', 'DB_USER_ID'))
