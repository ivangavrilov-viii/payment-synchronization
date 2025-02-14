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

# DATABASE CONNECTION
DB_NAME = config.get(CONFIG_DB, 'NAME')

DB_USER = config.get(CONFIG_DB, 'USER')

DB_HOST = config.get(CONFIG_DB, 'HOST')

DB_PORT = config.get(CONFIG_DB, 'PORT')

DB_PASSWORD = config.get(CONFIG_DB, 'PASSWORD')


# BASIC VARIABLES
GET_PAYMENTS = config.get('variables', 'GET_PAYMENTS_FUNC')

LANGUAGE = config.get('variables', 'LANGUAGE')

SERVICE_ID = int(config.get('variables', 'SERVICE_ID'))


# YOOKASSA kassa
YOOKASSA_ACCOUNT_ID = config.get(CONFIG_KASSA, 'YOOKASSA_ACCOUNT_ID')

YOOKASSA_SECRET_KEY = config.get(CONFIG_KASSA, 'YOOKASSA_SECRET_KEY')


# T-BANK kassa
TBANK_TERMINAL_KEY = config.get(CONFIG_KASSA, 'TBANK_TERMINAL_KEY')

TBANK_KASSA_URL = config.get(CONFIG_KASSA, 'TBANK_KASSA_URL')

TBANK_PASSWORD = config.get(CONFIG_KASSA, 'TBANK_PASSWORD')


# PAYSELECTIOM kassa
PAYSELECTION_PRIVATE_KEY = config.get(CONFIG_KASSA, 'PAYSELECTION_PRIVATE_KEY')

PAYSELECTION_SITE_ID = config.get(CONFIG_KASSA, 'PAYSELECTION_SITE_ID')

GW_API_URL = config.get(CONFIG_KASSA, 'GW_API_URL')
