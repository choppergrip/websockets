import json
import websockets


class WebSocketCoinBaseClient:
    def __init__(self, url):
        self.url = url
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.url)

    async def close(self):
        await self.websocket.close()

    async def subscribe(self, product_ids: list):
        subscribe_msg = {
            "type": "subscribe",
            "product_ids": product_ids,
            "channels": ["ticker"]
        }
        await self.send_message(subscribe_msg)
        response = await self.receive_message()
        return response

    async def send_message(self, message: dict):
        msg_json = json.dumps(message)
        await self.websocket.send(msg_json)

    async def receive_message(self):
        message = await self.websocket.recv()
        return json.loads(message)