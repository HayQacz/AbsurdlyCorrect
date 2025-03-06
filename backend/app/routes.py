import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.manager import ConnectionManager
from app.game_logic import Game
from app.models import GameSettings

router = APIRouter()
games = {}  # game_id -> Game
manager = ConnectionManager()

@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, game_id, player_id)
    global games
    if game_id != "nogame" and game_id not in games:
        games[game_id] = Game(game_id=game_id, host_id=player_id)
    game = games.get(game_id)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "create_game":
                nickname = data.get("nickname")
                new_game_id = str(uuid.uuid4())[:8]
                games[new_game_id] = Game(game_id=new_game_id, host_id=player_id)
                game = games[new_game_id]
                game.add_player(player_id, nickname)
                async def notify():
                    await manager.broadcast_game_state(game.id, games)
                    if game.game_phase == "presentation":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/presentation/{game.id}"})
                    elif game.game_phase == "voting":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/voting/{game.id}"})
                    elif game.game_phase == "selection" and game.current_round > 0:
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/game/{game.id}"})
                    elif game.game_phase == "results":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/results/{game.id}"})
                game.notify = notify
                if "nogame" in manager.active_connections:
                    conn = manager.active_connections["nogame"].pop(player_id, None)
                    if conn:
                        if new_game_id not in manager.active_connections:
                            manager.active_connections[new_game_id] = {}
                        manager.active_connections[new_game_id][player_id] = conn
                    if not manager.active_connections.get("nogame"):
                        manager.active_connections.pop("nogame", None)
                await manager.send_personal_message(
                    {"type": "game_update", "gameId": new_game_id, "playerId": player_id, "isHost": True},
                    websocket
                )
                await manager.send_personal_message(
                    {"type": "navigate", "route": f"/lobby/{new_game_id}"},
                    websocket
                )
            elif action == "join_game":
                nickname = data.get("nickname")
                join_game_id = data.get("gameId")
                if join_game_id not in games:
                    games[join_game_id] = Game(game_id=join_game_id, host_id=player_id)
                game = games[join_game_id]
                game.add_player(player_id, nickname)
                async def notify():
                    await manager.broadcast_game_state(game.id, games)
                    if game.game_phase == "presentation":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/presentation/{game.id}"})
                    elif game.game_phase == "voting":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/voting/{game.id}"})
                    elif game.game_phase == "selection" and game.current_round > 0:
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/game/{game.id}"})
                    elif game.game_phase == "results":
                        await manager.broadcast(game.id, {"type": "navigate", "route": f"/results/{game.id}"})
                game.notify = notify
                if "nogame" in manager.active_connections:
                    conn = manager.active_connections["nogame"].pop(player_id, None)
                    if conn:
                        if join_game_id not in manager.active_connections:
                            manager.active_connections[join_game_id] = {}
                        manager.active_connections[join_game_id][player_id] = conn
                    if not manager.active_connections.get("nogame"):
                        manager.active_connections.pop("nogame", None)
                await manager.send_personal_message(
                    {"type": "game_update", "gameId": join_game_id, "playerId": player_id, "isHost": False},
                    websocket
                )
                await manager.send_personal_message(
                    {"type": "navigate", "route": f"/lobby/{join_game_id}"},
                    websocket
                )
            elif action == "update_settings":
                newSettings = data.get("settings")
                if newSettings:
                    # Konwertujemy aktualne ustawienia na słownik, scalamy z nowymi, tworzymy nowy obiekt GameSettings
                    game.settings = GameSettings.parse_obj({**game.settings.dict(), **newSettings})
            elif action == "start_game":
                await game.start_game()
                await manager.broadcast(game.id, {"type": "navigate", "route": f"/game/{game.id}"})
            elif action == "restart_game":
                # Resetujemy stan gry – czyścimy odpowiedzi i głosy, ustawiamy rundę na 0 i fazę na lobby
                game.currentRound = 0
                game.game_phase = "lobby"
                game.player_answers.clear()
                game.votes.clear()
                # Broadcastujemy stan oraz przekierowujemy wszystkich do lobby
                await manager.broadcast_game_state(game.id, games)
                await manager.broadcast(game.id, {"type": "navigate", "route": f"/lobby/{game.id}"})
            elif action == "select_card":
                card_id = data.get("cardId")
                game.submit_answer(player_id, card_id)
            elif action == "vote":
                voted_player_id = data.get("votedPlayerId")
                game.submit_vote(player_id, voted_player_id)
            elif action == "leave_game":
                game.remove_player(player_id)
            await manager.broadcast_game_state(game.id, games)
    except WebSocketDisconnect:
        manager.disconnect(game_id, player_id)
