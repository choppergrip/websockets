import asyncio
import time
import pytest
from tests.constants import ProductIds, COINBASE_WS_FEED_URL
from tests.framework.latency_stats import analyze_2_data_feeds_latency, report_data_feeds_latency_stats
from tests.framework.latency_stats import calculate_percentiles
from tests.framework.logger import get_logger
from tests.framework.time_coversion import iso_to_timestamp
from websocket.clients.coinbase import WebSocketCoinBaseClient

logger = get_logger(__name__)

N_MESSAGES = 100
PERCENTILES = [50, 90, 95, 99]

async def collect_websocket_messages(client: WebSocketCoinBaseClient, n_messages: int):
    messages = []
    timestamps = []

    for _ in range(n_messages):
        msg = await client.receive_message()
        messages.append(msg)
        timestamps.append(time.time())

    return messages, timestamps


def match_messages_by_trade_id(messages_a: list, times_a: list, messages_b: list, times_b: list):
    matched = {}
    for msg, ts in zip(messages_a, times_a):
        trade_id = msg.get('trade_id')
        if trade_id:
            matched[trade_id] = {'A': ts - iso_to_timestamp(msg.get('time'))}

    for msg, ts in zip(messages_b, times_b):
        trade_id = msg.get('trade_id')
        if trade_id:
            if trade_id in matched:
                matched[trade_id]['B'] = ts - iso_to_timestamp(msg.get('time'))
            else:
                matched[trade_id] = {'B': ts - iso_to_timestamp(msg.get('time'))}

    assert len(matched) > 0, "No matching trade IDs found between messages_a and messages_b"

    return matched


class TestCoinbaseWebsocketTickerFeedPerformance:
    @pytest.mark.asyncio
    async def test_single_feed_receive_latency(self, coinbase_ws_client):
        client = coinbase_ws_client
        await client.subscribe([ProductIds.BTC_USD])

        ticker_messages, receive_times = await collect_websocket_messages(client, N_MESSAGES)

        latencies = []

        for msg, recv_time in zip(ticker_messages, receive_times):
            latency = (recv_time - iso_to_timestamp(msg.get("time"))) * 1000  # latency in ms
            latencies.append(latency)

        results = calculate_percentiles(latencies, PERCENTILES)
        logger.info("test_single_feed_receive_latency:")
        logger.info(f"Latency Percentiles (ms): {results}")

    @pytest.mark.asyncio
    async def test_ab_feeds_latency_comparison(self):
        client_a = WebSocketCoinBaseClient(COINBASE_WS_FEED_URL)
        client_b = WebSocketCoinBaseClient(COINBASE_WS_FEED_URL)

        await asyncio.gather(client_a.connect(), client_b.connect())
        await asyncio.gather(
            client_a.subscribe([ProductIds.BTC_USD]),
            client_b.subscribe([ProductIds.BTC_USD])
        )

        # collect messages concurrently
        (msgs_a, times_a), (msgs_b, times_b) = await asyncio.gather(
            collect_websocket_messages(client_a, N_MESSAGES),
            collect_websocket_messages(client_b, N_MESSAGES)
        )

        # we should compare only identical messages in both data feeds
        matched_msg = match_messages_by_trade_id(msgs_a, times_a, msgs_b, times_b)
        feeds_stats = analyze_2_data_feeds_latency(matched_msg, PERCENTILES)

        logger.info("test_ab_latency_comparison:")
        report_data_feeds_latency_stats(feeds_stats, logger)

        await asyncio.gather(client_a.close(), client_b.close())
