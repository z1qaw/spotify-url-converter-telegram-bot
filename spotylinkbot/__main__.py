import os
import logging

import telebot

from . import bot
from .utils import can_value_be_int

VAR_NAME_PREFIX = 'SPOTY_LINK_BOT_'
VAR_NAMES = {
    'TOKEN_VAR_NAME': 'TELEGRAM_TOKEN',
    'BOT_POLLING_INTERVAL_VAR_NAME': 'POLLING_INTERVAL',
    'DEBUG_VAR_NAME': 'DEBUG',
    'BOT_ADMINS_VAR_NAME': 'ADMINS_LIST',
    'SEND_START_MESSAGE_VAR_NAME': 'SEND_START_MESSAGE',
}

for key in VAR_NAMES:
    VAR_NAMES[key] = VAR_NAME_PREFIX + VAR_NAMES[key]

logger = telebot.logger
if os.environ.get(VAR_NAMES['DEBUG_VAR_NAME']) == 'true':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

try:
    assert VAR_NAMES['TOKEN_VAR_NAME'] in os.environ
except AssertionError as err:
    logger.exception('You must specify {} environment variable'.format(VAR_NAMES['TOKEN_VAR_NAME']))
    raise err

TELEGRAM_BOT_TOKEN = os.environ[VAR_NAMES['TOKEN_VAR_NAME']]

BOT_ADMINS = [int(admin_id) for admin_id in list(filter(can_value_be_int, os.environ.get(VAR_NAMES['BOT_ADMINS_VAR_NAME']).split(':')))]  \
                if os.environ.get(VAR_NAMES['BOT_ADMINS_VAR_NAME']) else []
BOT_ADMINS = list(set(BOT_ADMINS))

BOT_POLLING_INTERVAL = float(os.environ.get(VAR_NAMES['BOT_POLLING_INTERVAL_VAR_NAME']) or 0.2)
logger.info('Bot polling interval is ' + str(BOT_POLLING_INTERVAL))
if VAR_NAMES['BOT_POLLING_INTERVAL_VAR_NAME'] and BOT_POLLING_INTERVAL < 0.2:
    logger.warning('Bot polling interval doesn\'t recommended to be lower then 0.2')

BOT_SEND_START_MESSAGE = True if os.environ.get(VAR_NAMES['SEND_START_MESSAGE_VAR_NAME']) == 'true' else False

bot_instanse = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
spotylinkbot = bot.SpotyLinkBot(
    bot_instanse=bot_instanse,
    polling_interval=BOT_POLLING_INTERVAL,
    admin_chat_ids=BOT_ADMINS,
    send_start_message=BOT_SEND_START_MESSAGE
)

spotylinkbot.start()
