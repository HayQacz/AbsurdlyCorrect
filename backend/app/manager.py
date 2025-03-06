from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.game_logic import Game

class ConnectionManager:
    def __init__(self):
        # game_id -> {player_id: websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        print(f"DEBUG: connect -> game_id={game_id}, player_id={player_id}")
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        self.active_connections[game_id][player_id] = websocket

    def disconnect(self, game_id: str, player_id: str):
        print(f"DEBUG: disconnect -> game_id={game_id}, player_id={player_id}")
        if game_id in self.active_connections and player_id in self.active_connections[game_id]:
            del self.active_connections[game_id][player_id]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            if websocket.application_state == WebSocketState.CONNECTED:
                print(f"DEBUG: send_personal_message -> {message}")
                await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast(self, game_id: str, message: dict):
        print(f"DEBUG: broadcast -> game_id={game_id}, message={message}")
        if game_id in self.active_connections:
            for pid, wsock in list(self.active_connections[game_id].items()):
                try:
                    await self.send_personal_message(message, wsock)
                except Exception as e:
                    print(f"Error broadcasting to {pid}: {e}")
                    self.disconnect(game_id, pid)

    async def broadcast_game_state(self, game_id: str, games: Dict[str, Game]):
        print(f"DEBUG: broadcast_game_state -> game_id={game_id}")
        game = games.get(game_id)
        if not game:
            print("DEBUG: no such game_id in broadcast_game_state")
            return

        black_card_data = None
        if game.current_black_card:
            black_card_data = game.current_black_card.dict()

        players_data = [p.dict() for p in game.players]

        if game.game_phase in ["presentation", "voting", "results"]:
            answers_data = [ans.dict() for ans in game.player_answers]
        else:
            answers_data = []

        base_state = {
            "gameId": game.id,
            "players": players_data,
            "blackCard": black_card_data,
            "currentRound": game.current_round,
            "gamePhase": game.game_phase,
            "settings": game.settings.dict(),
            "playerAnswers": answers_data,
            "currentPresentationIndex": (
                game.current_presentation_index if game.game_phase == "presentation" else 0
            ),
            "timeLeft": game.timer_value,
        }

        if game.game_phase == "results":
            base_state["winners"] = [p.dict() for p in game.players[:3]]

        connections = self.active_connections.get(game.id, {})
        for pid, wsock in list(connections.items()):
            try:
                personal_state = dict(base_state)
                personal_state["playerId"] = pid
                personal_state["isHost"] = (pid == game.host_id)
                if game.game_phase == "selection":
                    card_list = game.player_cards.get(pid, [])
                    personal_state["whiteCards"] = [c.dict() for c in card_list]
                if game.game_phase == "voting":
                    if pid in game.votes:
                        personal_state["votedPlayerId"] = game.votes[pid]
                    else:
                        personal_state["votedPlayerId"] = None
                await self.send_personal_message({"type": "game_update", **personal_state}, wsock)
            except Exception as e:
                print(f"Error sending game state to {pid}: {e}")
                self.disconnect(game.id, pid)
