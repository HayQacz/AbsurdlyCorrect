from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

# SQLAlchemy Models
Base = declarative_base()

class BlackCardDB(Base):
    __tablename__ = 'black_cards'
    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)

class WhiteCardDB(Base):
    __tablename__ = 'white_cards'
    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)

# Pydantic Models
class BlackCard(BaseModel):
    id: str | None = None
    content: str

    class Config:
        orm_mode = True
        from_attributes = True

class WhiteCard(BaseModel):
    id: str | None = None
    content: str

    class Config:
        orm_mode = True
        from_attributes = True

class Player(BaseModel):
    id: str
    nickname: str
    score: int = 0

class PlayerAnswer(BaseModel):
    playerId: str
    nickname: str
    card: WhiteCard

class GameSettings(BaseModel):
    cardsPerPlayer: int = 5
    selectionTime: int = 15
    votingTime: int = 60
    maxPlayers: int = 10
