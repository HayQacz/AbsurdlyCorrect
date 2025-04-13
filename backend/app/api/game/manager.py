# file: app/game/manager.py

from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from app.api.game.logic import Game

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        await websocket.accept()
        self.active_connections.setdefault(game_id, {})[player_id] = websocket

    def disconnect(self, game_id: str, player_id: str):
        game_conns = self.active_connections.get(game_id)
        if game_conns:
            game_conns.pop(player_id, None)
            if not game_conns:
                self.active_connections.pop(game_id, None)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        if websocket.application_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(message)
            except Exception:
                pass

    async def broadcast(self, game_id: str, message: dict):
        for player_id, ws in self.active_connections.get(game_id, {}).items():
            await self.send_personal_message(message, ws)

    async def broadcast_game_state(self, game_id: str, games: Dict[str, Game]):
        game = games.get(game_id)
        if not game:
            return

        base_state = {
            "gameId": game.id,
            "players": [p.model_dump() for p in game.players],
            "blackCard": game.current_black_card.model_dump() if game.current_black_card else None,
            "currentRound": game.current_round,
            "gamePhase": game.game_phase,
            "settings": game.settings.model_dump(),
            "playerAnswers": [ans.model_dump() for ans in game.player_answers] if game.game_phase in ["presentation", "voting", "results"] else [],
            "currentPresentationIndex": game.current_presentation_index,
            "timeLeft": game.timer_value,
            "winners": [],
            "selectedCardId": None,
            "votedPlayerId": None,
            "votes": game.votes if game.game_phase == "voting" else {},
            "answersCount": len(game.player_answers) if game.game_phase == "selection" else 0
        }

        if game.game_phase == "results":
            base_state["winners"] = [p.model_dump() for p in game.players[:3]]

        for player_id, ws in self.active_connections.get(game.id, {}).items():
            personal_state = dict(base_state)
            personal_state["playerId"] = player_id
            personal_state["isHost"] = (player_id == game.host_id)
            if game.game_phase == "selection":
                personal_state["whiteCards"] = [c.model_dump() for c in game.player_cards.get(player_id, [])]
            if game.game_phase == "voting":
                personal_state["votedPlayerId"] = game.votes.get(player_id)
            await self.send_personal_message({"type": "game_update", **personal_state}, ws)
