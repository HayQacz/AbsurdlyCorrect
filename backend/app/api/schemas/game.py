from pydantic import BaseModel
from typing import List, Optional, Dict


class CreateGameRequest(BaseModel):
    nickname: str


class JoinGameRequest(BaseModel):
    gameId: str
    nickname: str


class UpdateSettingsRequest(BaseModel):
    settings: Dict[str, int]


class SelectCardRequest(BaseModel):
    cardId: str


class VoteRequest(BaseModel):
    votedPlayerId: str


class GameUpdate(BaseModel):
    type: str = "game_update"
    gameId: str
    playerId: str
    isHost: bool


class NavigateResponse(BaseModel):
    type: str = "navigate"
    route: str


class GameStateResponse(BaseModel):
    type: str = "game_update"
    gameId: str
    players: List[Dict]
    blackCard: Optional[Dict]
    currentRound: int
    gamePhase: str
    settings: Dict
    playerAnswers: List[Dict]
    currentPresentationIndex: int
    timeLeft: int
    winners: List[Dict]
    selectedCardId: Optional[str]
    votedPlayerId: Optional[str]
    votes: Optional[Dict]
    answersCount: Optional[int]
    playerId: str
    isHost: bool
    whiteCards: Optional[List[Dict]] = None
