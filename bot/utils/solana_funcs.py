from solana.rpc.async_api import AsyncClient
from solana.rpc.types import Pubkey, TokenAccountOpts
from solders.keypair import Keypair


async def get_balances(secret: list, client: AsyncClient):
    list_balances = []
    keypair = Keypair.from_bytes(bytes(secret))
    public_key = str(keypair.pubkey())

    balance_lamports = await client.get_balance(Pubkey.from_string(public_key))
    list_balances.append(str(balance_lamports.value / 1_000_000_000) + ' SOL')
    try:
        tokens_balances = await client.get_token_accounts_by_owner(owner=Pubkey.from_string(public_key),
                                                  opts=TokenAccountOpts(program_id=Pubkey.from_string(
                                                      'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')),
                                                  )
        for token in tokens_balances.value:
            b = bytes(token.account.data)
            mint = Pubkey.from_bytes(b[0:32])
            amount = int.from_bytes(b[64:72], "little")
            list_balances.append(str(amount) + ' ' + f'{str(mint)[:4]}...{str(mint)[-4:]}')
    except Exception as e:
        print(e)
        pass

    return list_balances, public_key
