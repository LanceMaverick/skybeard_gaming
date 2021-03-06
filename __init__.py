# from telegram.ext import CommandHandler, MessageHandler, Filters
import re
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from . import config, steam, overwatch

def remove_html(string):
    return re.sub('<[^<]+?>', '', string)

def sanitize_html(string):
    """Custom function to get rid of non-Telegram html"""
    # remove the extra href information
    string = string.replace('target="_blank"', '')
    string = re.sub(' +>', '>', string)

    # Standalone tags are not allowed
    string = re.sub(r'(<\w+ />)', '', string)

    # Remove tags that are not allowed
    allowed_tags = ['b', 'strong', 'i', 'em', 'a', 'code', 'pre']
    string = re.sub(r'(</?(?!{})[^/>]+>)'.format("|".join(allowed_tags)), '', string)
    return string


class Steam(BeardChatHandler):
    __userhelp__ = """
    Get news and patch notes for a game.
    Games currently configured:
    {}""".format(', '.join(k for k in config.game_ids.keys()))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_command('gamenews', self.game_news)

    async def game_news(self, msg):
        game_list = list(config.game_ids.keys())
        text = msg['text']
        game_list_str = '\n'.join(game_list)
        try:
            game = text.split('/gamenews',1)[1].strip()
        except IndexError:
            await self.sender.sendMessage(
                    'Please specify a steam game:\n'+game_list_str)
            return
        if game == 'overwatch':
            overwatch_news = overwatch.post_news()
            try:
                await self.sender.sendMessage(sanitize_html(overwatch_news), parse_mode='html')
            except telepot.exception.TelegramError:
                overwatch_news = remove_html(overwatch_news)
                await self.sender.sendMessage(overwatch_news)

        elif game not in game_list:
            await self.sender.sendMessage(
                    'Game not recognised. Please specify a steam game:\n'+game_list_str)
        else:
            game_id = config.game_ids[game]
            news = steam.post_news(game_id)
            try:
                await self.sender.sendMessage(sanitize_html(news), parse_mode='html')
            except telepot.exception.TelegramError:
                news = remove_html(news)
                await self.sender.sendMessage(news)
