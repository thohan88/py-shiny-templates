import websockets
import asyncio
import json
from .config import settings
from .database.database import get_db
from sqlalchemy.sql import text

async def vehicle_websocket_client(codespace_id, verbose=False, batch_size=10, reconnect_delay=2, max_reconnect_delay=30):
    ws_url = settings.entur_wss_url
    client_name = settings.entur_wss_client_name
    message_buffer = []

    async def log(message):
        if verbose:
            print(message)

    async def build_subscription_message():
        filter_clause = f'(codespaceId:"{codespace_id}")' if codespace_id != "ALL" else ""
        query = f'subscription {{ vehicles{filter_clause} {{ line {{ lineRef lineName publicCode }} mode lastUpdated location {{ latitude longitude }} vehicleId destinationName originName }} }}'
        return {"type": "start", "id": "1", "payload": {"query": query}}

    async def flush_buffer(session):
        if message_buffer:
            try:
                await log(f"Flushing {len(message_buffer)} messages")
                await session.execute(text("BEGIN TRANSACTION;"))
                for code, msg in message_buffer:
                    await session.execute(
                        text("INSERT INTO ENTUR_RAW (codespace_id, message) VALUES (:codespace_id, :message)"),
                        {"codespace_id": code, "message": msg},
                    )
                await session.commit()
                message_buffer.clear()
            except Exception as e:
                await log(f"Error flushing buffer: {e}")
                await session.rollback()
                raise

    async def receive_messages(websocket, session):
        try:
            async for message in websocket:
                await log(f"Received: {message}")
                try:
                    json.loads(message)  # Validate JSON
                    message_buffer.append((codespace_id, message))
                    if len(message_buffer) >= batch_size:
                        await flush_buffer(session)
                except json.JSONDecodeError:
                    await log("Invalid JSON")
        except websockets.ConnectionClosed:
            await log("Connection closed")
            raise

    while True:
        try:
            await log(f"Connecting to {ws_url}")
            async with websockets.connect(ws_url, subprotocols=["graphql-ws"], additional_headers={"ET-Client-Name": client_name}) as websocket:
                await log("Connected")
                await websocket.send(json.dumps(await build_subscription_message()))
                reconnect_delay = 2  # Reset delay on success

                async for session in get_db():
                    await log("Database session created")
                    await receive_messages(websocket, session)

        except (websockets.ConnectionClosed, websockets.WebSocketException) as e:
            await log(f"WebSocket error: {e}. Reconnecting in {reconnect_delay}s...")
        except Exception as e:
            await log(f"Unexpected error: {e}")
            raise

        await asyncio.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)