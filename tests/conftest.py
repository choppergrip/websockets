import pytest_asyncio
from tests.constants import COINBASE_WS_FEED_URL
from websocket.clients.coinbase import WebSocketCoinBaseClient


@pytest_asyncio.fixture()
async def coinbase_ws_client():
    client = WebSocketCoinBaseClient(COINBASE_WS_FEED_URL)
    await client.connect()
    yield client
    await client.close()
