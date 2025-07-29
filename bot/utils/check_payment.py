import asyncio
import json, os
from decimal import getcontext, Decimal

from dotenv import load_dotenv
from pytonapi import AsyncTonapi
from solana.rpc.async_api import AsyncClient
from solana.exceptions import SolanaRpcException
from solana.rpc.types import Pubkey
from spl.token.instructions import get_associated_token_address


load_dotenv()

tonapi = AsyncTonapi(api_key=os.getenv('API_KEY_TON'))


async def check_payment_ton(amount: str):
    getcontext().prec = 18
    your_amount_dec = Decimal(amount)
    your_amount_nano = int((your_amount_dec * Decimal(10 ** 9)).to_integral_value())

    transactions = await tonapi.accounts.get_events(account_id=os.getenv('TON_ADDRESS'), limit=15)
    for tx in transactions.events:
        if tx.actions[0].TonTransfer is None:
            continue
        if tx.actions[0].TonTransfer.amount == your_amount_nano:
            return True


async def check_payment_sol(amount: str, client: AsyncClient):
    ata = get_associated_token_address(mint=Pubkey.from_string(os.getenv('MINT_TOKEN_ADDRESS')), owner=Pubkey.from_string(os.getenv('ADDRESS_SOL')))

    getcontext().prec = 18
    your_amount_dec = Decimal(amount)

    bal_info = await client.get_token_account_balance(ata, commitment="confirmed")
    decimals = bal_info.value.decimals
    your_amount_nano = int((your_amount_dec * Decimal(10 ** decimals)).to_integral_value())

    sigs = await client.get_signatures_for_address(ata, limit=10)
    for sig in sigs.value:
        await asyncio.sleep(0.5)
        while True:
            try:
                transaction = await client.get_transaction(sig.signature, encoding="jsonParsed",
                                                           max_supported_transaction_version=0)
                instructions = transaction.value.transaction.transaction.message.instructions
                for index, instr in enumerate(instructions):
                    data_instr = json.loads(instr.to_json())
                    if data_instr.get("program") != "spl-token":
                        continue
                    if data_instr['parsed']['info']['destination'] == str(ata) and \
                            data_instr['parsed']['info']['tokenAmount']['amount'] == str(your_amount_nano):
                        return True
                break
            except SolanaRpcException as e:
                await asyncio.sleep(5)
            except Exception as e:
                return False
    return False

