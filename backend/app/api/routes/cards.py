# file: app/api/routes/cards.py

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.db.database import get_session
from app.api.db.models import BlackCardDB, WhiteCardDB, BlackCard, WhiteCard

router = APIRouter()


@router.get("/black_cards", response_model=List[BlackCard])
async def get_black_cards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB))
    cards = result.scalars().all()
    return [BlackCard.model_validate(card) for card in cards]


@router.post("/black_cards", response_model=BlackCard)
async def create_black_card(card: BlackCard, session: AsyncSession = Depends(get_session)):
    data = card.model_dump()
    data["id"] = data.get("id") or str(uuid.uuid4())
    db_card = BlackCardDB(**data)
    session.add(db_card)
    await session.commit()
    await session.refresh(db_card)
    return BlackCard.model_validate(db_card)


@router.put("/black_cards/{card_id}", response_model=BlackCard)
async def update_black_card(card_id: str, card_data: BlackCard, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB).where(BlackCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.content = card_data.content
    await session.commit()
    await session.refresh(db_card)
    return BlackCard.model_validate(db_card)


@router.delete("/black_cards/{card_id}")
async def delete_black_card(card_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BlackCardDB).where(BlackCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    await session.delete(db_card)
    await session.commit()
    return {"detail": "Card deleted"}


@router.get("/white_cards", response_model=List[WhiteCard])
async def get_white_cards(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB))
    cards = result.scalars().all()
    return [WhiteCard.model_validate(card) for card in cards]


@router.post("/white_cards", response_model=WhiteCard)
async def create_white_card(card: WhiteCard, session: AsyncSession = Depends(get_session)):
    data = card.model_dump()
    data["id"] = data.get("id") or str(uuid.uuid4())
    db_card = WhiteCardDB(**data)
    session.add(db_card)
    await session.commit()
    await session.refresh(db_card)
    return WhiteCard.model_validate(db_card)


@router.put("/white_cards/{card_id}", response_model=WhiteCard)
async def update_white_card(card_id: str, card_data: WhiteCard, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB).where(WhiteCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.content = card_data.content
    await session.commit()
    await session.refresh(db_card)
    return WhiteCard.model_validate(db_card)


@router.delete("/white_cards/{card_id}")
async def delete_white_card(card_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WhiteCardDB).where(WhiteCardDB.id == card_id))
    db_card = result.scalars().first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    await session.delete(db_card)
    await session.commit()
    return {"detail": "Card deleted"}
