import logging
import logging.config
from telegram import Bot
import os

ADMIN_ID = "305197734"
BOT_KEY = "5133601045:AAH8FIsPniGeoLK-8yo59wjEbX15VKqNAyM"

class TelegramBotHandler(logging.Handler):
    def __init__(self):
        self.ADMIN_ID = ADMIN_ID
        self.BOT_KEY = BOT_KEY        
        super().__init__()

    def emit(self, record: logging.LogRecord):
        try:
            Bot(self.BOT_KEY).send_message(int(self.ADMIN_ID), str(self.format(record)))
        except Exception as ex:
            logger.debug(f"Previous report was not sent by Telegram, cause: {str(ex)}")

toplevel = 'server'
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.FileHandler',
            'filename': os.path.dirname(__file__) + '/logs.txt',
            'level': 'DEBUG',
            'formatter': 'default_formatter'
        },
        'simple_stream_handler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default_formatter'
        },
        'telegram_handler': {
            'class': '__main__.TelegramBotHandler',
            'level': 'WARNING',
            'formatter': 'default_formatter'
        }
    },

    'loggers': {
        toplevel: {
            'handlers': ['stream_handler', 'telegram_handler', 'simple_stream_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

class LoggerWrapper:
    def __init__(self, logger):
        self.logger = logger
        self.ADMIN_ID = ADMIN_ID
        self.BOT_KEY = BOT_KEY
    def sendFile(self, filepath):
        try:
            Bot(self.BOT_KEY).send_document(
                int(self.ADMIN_ID),
                open(filepath, 'rb'),
                filename=os.path.basename(filepath)
            )
            self.logger.debug(f"File {filepath} has just been sent")
        except Exception as ex:
            self.logger.error(f"File wasn't sent, error {ex}")
    def __getattr__(self, attr):
        if (attr == 'sendFile'):
            return self.sendFile
        return self.logger.__getattribute__(attr)  
