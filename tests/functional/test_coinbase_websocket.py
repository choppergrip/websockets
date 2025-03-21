import pytest
from tests.constants import ProductIds
from websocket.models.coinbase.ticker_subscription_messages import SubscriptionResponse, TickerMessage, SubscribeError


async def _assert_error_response(response: dict, reason: str):
    error = SubscribeError.model_validate(response)
    assert error.type == "error"
    assert error.message == "Failed to subscribe"
    assert error.reason == reason


class TestCoinbaseWebsocket:
    @pytest.mark.asyncio
    async def test_successful_subscription(self, coinbase_ws_client):
        client = coinbase_ws_client
        subscription_response = await client.subscribe([ProductIds.BTC_USD])
        SubscriptionResponse.model_validate(subscription_response)

        # Check first 3 messages
        n_messages = 3
        for _ in range(n_messages):
            message = await client.receive_message()
            validated_message = TickerMessage.model_validate(message)
            assert validated_message.product_id == ProductIds.BTC_USD

    @pytest.mark.asyncio
    async def test_subscribe_multiple_tickers(self, coinbase_ws_client):
        client = coinbase_ws_client
        tickers = [ProductIds.BTC_USD, ProductIds.ETH_USD]
        subscription_response = await client.subscribe(tickers)
        SubscriptionResponse.model_validate(subscription_response)

        messages = []
        n_messages = 35
        while len(messages) < n_messages:
            msg = await client.receive_message()
            TickerMessage.model_validate(msg)
            messages.append(msg)

        received_tickers = set(msg.get('product_id') for msg in messages)

        assert received_tickers.issuperset(set(tickers)), (
            f"Expected tickers: {tickers}, but only received updates for: {received_tickers}"
        )

    @pytest.mark.asyncio
    async def test_no_duplicate_messages_on_double_subscription(self, coinbase_ws_client):
        client = coinbase_ws_client

        await client.subscribe([ProductIds.BTC_USD, ProductIds.BTC_USD])

        sequences = set()
        trade_ids = set()

        n_messages = 10

        for _ in range(n_messages):
            message = await client.receive_message()
            validated_message = TickerMessage.model_validate(message)
            assert validated_message.product_id == ProductIds.BTC_USD

            # Check for duplicate sequence numbers
            assert validated_message.sequence not in sequences, f"Duplicate sequence found: {validated_message.sequence}"
            sequences.add(validated_message.sequence)

            # Check for duplicate trade_ids
            assert validated_message.trade_id not in trade_ids, f"Duplicate trade_id found: {validated_message.trade_id}"
            trade_ids.add(validated_message.trade_id)


    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, expected_reason",
        [
            ([], " is not a valid product"),
            (["Test"], "Test is not a valid product"),
            ("INVALID-TICKER", "Invalid product ID provided"),
        ]
    )
    async def test_invalid_ticker_subscriptions(self, coinbase_ws_client, payload, expected_reason):
        client = coinbase_ws_client
        response = await client.subscribe(payload)
        await _assert_error_response(
            response,
            reason=expected_reason
        )

    @pytest.mark.asyncio
    async def test_missing_fields_subscription(self, coinbase_ws_client):
        client = coinbase_ws_client
        # sending malformed payload manually
        await client.send_message({"action": "subscribe"})
        response = await client.receive_message()

        await _assert_error_response(
            response,
            reason="Type has to be either subscribe or unsubscribe"
        )
