import os
import threading
import time
from typing import Union

import telebot
from telebot import types

from . import spotify_links
from .utils import escape_markdown

logger = telebot.logger

class SpotyLinkBot(threading.Thread):
    def __init__(self, bot_instanse: telebot.TeleBot, polling_interval: float,
                    error_reload_interval: int, admin_chat_ids: Union[None, list] = None,
                    send_start_message: bool = False) -> None:
        super().__init__()
        self.bot = bot_instanse
        self.polling_interval = polling_interval
        self.admin_chat_ids = list(set(admin_chat_ids))
        self.error_reload_interval = error_reload_interval

        if self.admin_chat_ids and send_start_message:
            for id in self.admin_chat_ids:
                self.bot.send_message(id, 'Bot started')
                logger.info(f'Send start message to admin with ID {id}')

    def start_polling(self) -> None:
        @self.bot.inline_handler(
            func=lambda query: spotify_links.ITEM_LINK_PATTERN.match(query.query)
        )
        def handle_item_link_to_spotify_url_inline(query):
            logger.info(f'Inline query {query.id} with item link')
            logger.info(query)
            converted_url = spotify_links.convert_item_link_to_spotify(query.query)
            this_link_query_result = types.InlineQueryResultArticle(
                id=1, title='Don\'t convert, just send link', description=query.query[:36] + '...',
                input_message_content=types.InputTextMessageContent(
                message_text=query.query)
            )
            converted_url_query_result = types.InlineQueryResultArticle(
                id=2, title='Send converted Spotify URL', description=converted_url,
                input_message_content=types.InputTextMessageContent(
                message_text=f'`{escape_markdown(converted_url)}`', parse_mode='Markdown')
            )
            combined_links_query_result = types.InlineQueryResultArticle(
                id=3, title='Send combined result', description='Your link + it\'s Spotify URL',
                input_message_content=types.InputTextMessageContent(
                message_text=f'`{escape_markdown(converted_url)}`\n\n' + escape_markdown(query.query), parse_mode='Markdown'))

            logger.info(f'Send inline answer to query {query.id}')

            self.bot.answer_inline_query(query.id, [
                this_link_query_result,
                converted_url_query_result,
                combined_links_query_result
            ])

        @self.bot.inline_handler(
            func=lambda query: spotify_links.SPOTIFY_ITEM_URL_PATTERN.match(query.query)
        )
        def handle_item_spotify_url_to_link_inline(query):
            logger.info(f'Inline query {query.id} with item link')
            logger.info(query)
            converted_link = spotify_links.convert_item_spotify_url_to_link(query.query)
            this_spotify_url_query_result = types.InlineQueryResultArticle(
                id=1, title='Don\'t convert, just send Spotify URL', description=query.query,
                input_message_content=types.InputTextMessageContent(
                message_text=query.query)
            )
            converted_link_query_result = types.InlineQueryResultArticle(
                id=2, title='Send converted link', description=converted_link[:36] + '...',
                input_message_content=types.InputTextMessageContent(
                message_text=f'`{escape_markdown(converted_link)}`', parse_mode='Markdown')
            )
            combined_links_query_result = types.InlineQueryResultArticle(
                id=3, title='Send combined result', description='Your Spotify URL + it\'s link',
                input_message_content=types.InputTextMessageContent(
                message_text=f'`{escape_markdown(query.query)}`\n\n' + escape_markdown(converted_link), parse_mode='Markdown'))

            logger.info(f'Send inline answer to query {query.id}')
            self.bot.answer_inline_query(query.id, [
                this_spotify_url_query_result,
                converted_link_query_result,
                combined_links_query_result
            ])

        @self.bot.inline_handler(func=lambda query: True)
        def catch_every_inline_message(query):
            logger.info('Bot catched strange inline query.')
            logger.debug(query)

        @self.bot.message_handler(commands=['start'])
        def handle_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            self.bot.reply_to(
                message,
                'Hello!👽\n' + \
                'This bot will help you to convert Spotify links. 🙌🏾\n\n' + \
                'Type /help to see more info about it!'
            )

        @self.bot.message_handler(commands=['help'])
        def handle_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            self.bot.reply_to(
                message,
                'To convert any link from this:\n\n' + \
                '`spotify:track:xxxxxxxxxxxxxxxxxx`\n\n' + \
                'To this:\n\n' + \
                '`https://open.spotify.com/track/xxxxxxxxxxxxxxxxx`\n\n' + \
                'and vice versa, just send your link in any format to this bot in chat or using ' + \
                'inline mode in any chat you need!', parse_mode='Markdown'
            )
            self.bot.send_photo(
                message.chat.id,
                open(os.path.join('spotylinkbot', 'images', 'inline_help.jpg'), 'rb')
            )

        @self.bot.message_handler(
            content_types=['text'],
            func=lambda message: spotify_links.SPOTIFY_ITEM_URL_PATTERN.match(message.text))
        def handle_item_spotify_url_to_link(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')

            converted_link = spotify_links.convert_item_spotify_url_to_link(message.text)
            self.bot.reply_to(message, text=converted_link, parse_mode='Markdown')

        @self.bot.message_handler(
            content_types=['text'],
            func=lambda message: spotify_links.ITEM_LINK_PATTERN.match(message.text))
        def handle_item_spotify_url_to_link(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')

            converted_link = spotify_links.convert_item_link_to_spotify(message.text)
            self.bot.reply_to(message, text=f'`{converted_link}`', parse_mode='Markdown')

        @self.bot.message_handler(func=lambda message: True)
        def handle_strange_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New strange message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            logger.debug(message)

            self.bot.reply_to(message, text='Send me valid Spotify Link or URL 🧐')
        
        self.bot.polling(none_stop=True, interval=self.polling_interval)

    def run(self) -> None:
        while True:
            try:
                self.start_polling()
            except Exception as err:
                logger.error(err)
                logger.info(f'Reload bot polling in {self.error_reload_interval} seconds')
                time.sleep(self.error_reload_interval)
