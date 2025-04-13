import pytest
import json
import uuid
import websockets
import asyncio

WEBSOCKET_URL = "ws://localhost:8000/ws/nogame/"


@pytest.mark.asyncio
async def test_create_game_websocket():
    player_id = str(uuid.uuid4())

    async with websockets.connect(WEBSOCKET_URL + player_id) as websocket:
        await websocket.send(json.dumps({
            "action": "create_game",
            "nickname": "Tester"
        }))

        response = await websocket.recv()
        message = json.loads(response)

        assert message["type"] == "game_update"
        assert message["playerId"] == player_id
        assert message["isHost"] is True
        assert "gameId" in message

        response = await websocket.recv()
        nav = json.loads(response)

        assert nav["type"] == "navigate"
        assert nav["route"].startswith("/lobby/")
