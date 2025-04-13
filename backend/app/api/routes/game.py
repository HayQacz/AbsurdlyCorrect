# file: app/api/routes/game.py

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.game.logic import Game
from app.api.game.manager import ConnectionManager
from app.api.db.models import GameSettings
from app.api.schemas.game import GameUpdate, NavigateResponse

router = APIRouter()
games: dict[str, Game] = {}
manager = ConnectionManager()


@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, game_id, player_id)

    if game_id != "nogame" and game_id not in games:
        games[game_id] = Game(game_id=game_id, host_id=player_id)

    game = games.get(game_id)

    def setup_notify():
        async def notify():
            await manager.broadcast_game_state(game.id, games)
            route = None
            if game.game_phase == "presentation":
                route = f"/presentation/{game.id}"
            elif game.game_phase == "voting":
                route = f"/voting/{game.id}"
            elif game.game_phase == "selection" and game.current_round > 0:
                route = f"/game/{game.id}"
            elif game.game_phase == "results":
                route = f"/results/{game.id}"
            if route:
                await manager.broadcast(game.id, NavigateResponse(route=route).model_dump())
        game.notify = notify

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "create_game":
                nickname = data["nickname"]
                new_game_id = str(uuid.uuid4())[:8]
                games[new_game_id] = Game(game_id=new_game_id, host_id=player_id)
                game = games[new_game_id]
                game.add_player(player_id, nickname)
                setup_notify()

                conn = manager.active_connections.get("nogame", {}).pop(player_id, None)
                if conn:
                    manager.active_connections.setdefault(new_game_id, {})[player_id] = conn
                if not manager.active_connections.get("nogame"):
                    manager.active_connections.pop("nogame", None)

                await manager.send_personal_message(
                    GameUpdate(gameId=new_game_id, playerId=player_id, isHost=True).model_dump(),
                    websocket
                )
                await manager.send_personal_message(
                    NavigateResponse(route=f"/lobby/{new_game_id}").model_dump(),
                    websocket
                )

            elif action == "join_game":
                nickname = data["nickname"]
                join_game_id = data["gameId"]
                if join_game_id not in games:
                    games[join_game_id] = Game(game_id=join_game_id, host_id=player_id)
                game = games[join_game_id]
                game.add_player(player_id, nickname)
                setup_notify()

                conn = manager.active_connections.get("nogame", {}).pop(player_id, None)
                if conn:
                    manager.active_connections.setdefault(join_game_id, {})[player_id] = conn
                if not manager.active_connections.get("nogame"):
                    manager.active_connections.pop("nogame", None)

                await manager.send_personal_message(
                    GameUpdate(gameId=join_game_id, playerId=player_id, isHost=False).model_dump(),
                    websocket
                )
                await manager.send_personal_message(
                    NavigateResponse(route=f"/lobby/{join_game_id}").model_dump(),
                    websocket
                )

            elif action == "update_settings":
                new_settings = data.get("settings")
                if new_settings:
                    merged = {**game.settings.model_dump(), **new_settings}
                    game.settings = GameSettings.model_validate(merged)

            elif action == "start_game":
                await game.start_game()
                await manager.broadcast(game.id, NavigateResponse(route=f"/game/{game.id}").model_dump())

            elif action == "restart_game":
                game.current_round = 0
                game.game_phase = "lobby"
                game.player_answers.clear()
                game.votes.clear()
                await manager.broadcast_game_state(game.id, games)
                await manager.broadcast(game.id, NavigateResponse(route=f"/lobby/{game.id}").model_dump())

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
