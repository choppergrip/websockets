from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class Channel(BaseModel):
    name: Literal["ticker"]
    product_ids: List[str]
    account_ids: None

class SubscriptionResponse(BaseModel):
    type: Literal["subscriptions"]
    channels: List[Channel]

class TickerMessage(BaseModel):
    type: Literal["ticker"]
    sequence: int
    product_id: str
    price: str
    open_24h: str
    volume_24h: str
    low_24h: str
    high_24h: str
    volume_30d: str
    best_bid: str
    best_bid_size: str
    best_ask: str
    best_ask_size: str
    side: Literal["buy", "sell"]
    time: datetime
    last_size: str
    trade_id: int
    last_size: str

class SubscribeError(BaseModel):
    type: Literal["error"]
    message: str
    reason: str