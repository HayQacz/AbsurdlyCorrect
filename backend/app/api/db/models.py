from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, ConfigDict

Base = declarative_base()

# --- DB Models ---

class BlackCardDB(Base):
    __tablename__ = "black_cards"
    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)

class WhiteCardDB(Base):
    __tablename__ = "white_cards"
    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)

# --- Pydantic Models ---

class BlackCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str | None = None
    content: str

class WhiteCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str | None = None
    content: str

class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nickname: str
    score: int = 0

class PlayerAnswer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    playerId: str
    nickname: str
    card: WhiteCard

class GameSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cardsPerPlayer: int = 5
    selectionTime: int = 15
    votingTime: int = 60
    maxPlayers: int = 10
