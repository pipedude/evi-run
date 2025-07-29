import os
import sys

from dotenv import load_dotenv
from aiohttp import ClientSession, ClientTimeout
from aiogram import Bot

from config import TYPE_USAGE, ADMIN_ID, HOST_ADDRESS

load_dotenv()


async def add_burn_address(bot: Bot):
    if TYPE_USAGE == 'pay':
        if (not os.getenv('TOKEN_BURN_ADDRESS')) or (not ADMIN_ID):
            await bot.send_message(chat_id=ADMIN_ID,
                                   text='The bot is not running! To activate the "pay"" mode, you must pass a check, see the documentation for details!')
            sys.exit(1)

        async with ClientSession(timeout=ClientTimeout(60)) as session:
            url = f"{HOST_ADDRESS}/create_payment_module"
            json = {
                "token_burn_address": os.getenv('TOKEN_BURN_ADDRESS'),
                "user_id": ADMIN_ID
            }
            try:
                async with session.post(url, json=json, ssl=False) as response:
                    data = await response.json()
                    if data['status'] == 'error':
                        await bot.send_message(chat_id=ADMIN_ID,
                                               text='The bot is not running! To activate the "pay"" mode, you must pass a check, see the documentation for details!')
                        sys.exit(1)

            except Exception as e:
                await bot.send_message(chat_id=ADMIN_ID,
                                       text='The bot is not running! To activate the "pay"" mode, you must pass a check, see the documentation for details!')
                sys.exit(1)

            try:
                url = f'{HOST_ADDRESS}/check_balance'
                async with session.post(url, json=json, ssl=False) as response:
                    data = await response.json()
                    if data['status'] == 'error':
                        await bot.send_message(chat_id=ADMIN_ID,
                                               text='The bot is not running! To activate the "pay"" mode, you must pass a check, see the documentation for details!')
                        sys.exit(1)

            except Exception as e:
                await bot.send_message(chat_id=ADMIN_ID,
                                       text='The bot is not running! To activate the "pay"" mode, you must pass a check, see the documentation for details!')
                sys.exit(1)

