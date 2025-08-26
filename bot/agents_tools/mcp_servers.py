import json

from collections import OrderedDict

import base58
from agents.mcp import MCPServerStdio

MAX_SERVERS = 20

servers: OrderedDict[str, MCPServerStdio] = OrderedDict()
global_dexpaprika_server = None


async def get_dexpapirka_server():
    global global_dexpaprika_server
    if global_dexpaprika_server:
        return global_dexpaprika_server

    dexpaprika_server = MCPServerStdio(
        name="DexPaprika",
        params={
            "command": "dexpaprika-mcp",
            "args": [],
        }
    )
    await dexpaprika_server.connect()
    global_dexpaprika_server = dexpaprika_server
    return dexpaprika_server


async def get_jupiter_server(private_key: str, user_id: int):
    srv = servers.get(user_id)
    if srv:
        servers.move_to_end(user_id)
        return srv

    secret_bytes = bytes(json.loads(private_key))
    private_key_b58 = base58.b58encode(secret_bytes).decode()

    srv = MCPServerStdio(
        name=f"jupiter-{user_id}",
        params={
            "command": "node",
            "args": ['/usr/lib/node_modules/jupiter-mcp/index.js'],
            "env": {
                "PRIVATE_KEY": private_key_b58,
                "SOLANA_RPC_URL": 'https://api.mainnet-beta.solana.com',
            },
        },
        cache_tools_list=True,
    )
    await srv.connect()
    servers[user_id] = srv

    if len(servers) > MAX_SERVERS:
        old_key, old_srv = servers.popitem(last=False)
        await old_srv.cleanup()

    return srv
