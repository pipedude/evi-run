from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='General information'),
        BotCommand(command='new', description='Start a new chat'),
        BotCommand(command='save', description='Save the chat in memory'),
        BotCommand(command='delete', description='Clear the agent’s memory'),
        BotCommand(command='balance', description='Balance in the bot'),
        BotCommand(command='settings', description='Settings'),
        BotCommand(command='wallet', description='Agent’s wallet for trading'),
        BotCommand(command='help', description='Help'),
        BotCommand(command='knowledge', description='Add knowledge to the agent’s memory'),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())