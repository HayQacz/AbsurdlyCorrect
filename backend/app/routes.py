import uuid
import asyncio
from typing import List, AsyncGenerator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.manager import ConnectionManager
from app.game_logic import Game
from app.models import (
    BlackCardDB,
    WhiteCardDB,
    BlackCard,
    WhiteCard,
    GameSettings
)
from app.database import async_session

router = APIRouter()
games = {}  # game_id -> Game
manager = ConnectionManager()

# Dependency: zwraca asynchroniczną sesję
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# -------------------------------
# WebSocket endpoint (obsługa gry)
# -------------------------------
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
                    updated_settings = {**game.settings.dict(), **newSettings}
                    game.settings = GameSettings.parse_obj(updated_settings)

            elif action == "start_game":
                await game.start_game()
                await manager.broadcast(game.id, {"type": "navigate", "route": f"/game/{game.id}"})

            elif action == "restart_game":
                game.currentRound = 0
                game.game_phase = "lobby"
                game.player_answers.clear()
                game.votes.clear()
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


# -------------------------------
# CRUD Endpoints for Black Cards
# -------------------------------
crud_router = APIRouter()

@crud_router.get("/black_cards", response_model=List[BlackCard])
async def get_black_cards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB))
    cards = result.scalars().all()
    return [BlackCard.from_orm(card) for card in cards]

@crud_router.post("/black_cards", response_model=BlackCard)
async def create_black_card(card: BlackCard, session: AsyncSession = Depends(get_session)):
    data = card.dict()
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())
    db_card = BlackCardDB(**data)
    session.add(db_card)
    await session.commit()
    await session.refresh(db_card)
    return BlackCard.from_orm(db_card)

@crud_router.put("/black_cards/{card_id}", response_model=BlackCard)
async def update_black_card(card_id: str, card_data: BlackCard, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB).where(BlackCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.content = card_data.content
    await session.commit()
    await session.refresh(db_card)
    return BlackCard.from_orm(db_card)

@crud_router.delete("/black_cards/{card_id}")
async def delete_black_card(card_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB).where(BlackCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    await session.delete(db_card)
    await session.commit()
    return {"detail": "Card deleted"}


# -------------------------------
# CRUD Endpoints for White Cards
# -------------------------------
@crud_router.get("/white_cards", response_model=List[WhiteCard])
async def get_white_cards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB))
    cards = result.scalars().all()
    return [WhiteCard.from_orm(card) for card in cards]

@crud_router.post("/white_cards", response_model=WhiteCard)
async def create_white_card(card: WhiteCard, session: AsyncSession = Depends(get_session)):
    data = card.dict()
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())
    db_card = WhiteCardDB(**data)
    session.add(db_card)
    await session.commit()
    await session.refresh(db_card)
    return WhiteCard.from_orm(db_card)

@crud_router.put("/white_cards/{card_id}", response_model=WhiteCard)
async def update_white_card(card_id: str, card_data: WhiteCard, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB).where(WhiteCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.content = card_data.content
    await session.commit()
    await session.refresh(db_card)
    return WhiteCard.from_orm(db_card)

@crud_router.delete("/white_cards/{card_id}")
async def delete_white_card(card_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB).where(WhiteCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    await session.delete(db_card)
    await session.commit()
    return {"detail": "Card deleted"}

router.include_router(crud_router)
