# file: app/game/logic.py

import random
import asyncio
from typing import List, Dict, Optional, Callable, Awaitable
from fastapi import WebSocket

from app.api.db.models import (
    BlackCard,
    WhiteCard,
    Player,
    PlayerAnswer,
    GameSettings,
    BlackCardDB,
    WhiteCardDB,
)
from sqlalchemy import select
from app.api.db.database import async_session

class Game:
    def __init__(self, game_id: str, host_id: str):
        self.id = game_id
        self.host_id = host_id
        self.players: List[Player] = []
        self.black_cards: List[BlackCard] = []
        self.white_cards: List[WhiteCard] = []
        self.used_black_cards: List[BlackCard] = []
        self.used_white_cards: List[WhiteCard] = []
        self.player_cards: Dict[str, List[WhiteCard]] = {}
        self.current_black_card: Optional[BlackCard] = None
        self.player_answers: List[PlayerAnswer] = []
        self.votes: Dict[str, str] = {}
        self.current_round = 0
        self.round_winners: List[str] = []
        self.game_phase = "lobby"
        self.settings = GameSettings()
        self.connections: Dict[str, WebSocket] = {}
        self.timer_task: Optional[asyncio.Task] = None
        self.presentation_task: Optional[asyncio.Task] = None
        self.current_presentation_index = 0
        self.timer_value = 0
        self.notify: Optional[Callable[[], Awaitable[None]]] = None

    async def load_cards(self):
        async with async_session() as session:
            black_result = await session.execute(select(BlackCardDB))
            white_result = await session.execute(select(WhiteCardDB))
            self.black_cards = [BlackCard.model_validate(card) for card in black_result.scalars().all()]
            self.white_cards = [WhiteCard.model_validate(card) for card in white_result.scalars().all()]
        random.shuffle(self.black_cards)
        random.shuffle(self.white_cards)

    def add_player(self, player_id: str, nickname: str) -> Player:
        if any(p.id == player_id for p in self.players):
            return next(p for p in self.players if p.id == player_id)
        if len(self.players) >= self.settings.maxPlayers:
            raise ValueError("Game is full")
        if any(p.nickname == nickname for p in self.players):
            nickname += f"_{random.randint(1, 999)}"
        player = Player(id=player_id, nickname=nickname)
        self.players.append(player)
        return player

    def remove_player(self, player_id: str):
        self.players = [p for p in self.players if p.id != player_id]
        self.connections.pop(player_id, None)
        if player_id == self.host_id and self.players:
            self.host_id = self.players[0].id
        if len(self.players) < 2 and self.game_phase != "lobby":
            self.end_game()

    def deal_cards(self):
        for player in self.players:
            if len(self.white_cards) < self.settings.cardsPerPlayer:
                self.white_cards.extend(self.used_white_cards)
                self.used_white_cards.clear()
                random.shuffle(self.white_cards)
            hand = [self.white_cards.pop(0) for _ in range(self.settings.cardsPerPlayer) if self.white_cards]
            self.player_cards[player.id] = hand

    def select_black_card(self):
        if not self.black_cards:
            self.black_cards.extend(self.used_black_cards)
            self.used_black_cards.clear()
            random.shuffle(self.black_cards)
        if self.black_cards:
            self.current_black_card = self.black_cards.pop(0)
            self.used_black_cards.append(self.current_black_card)

    def submit_answer(self, player_id: str, card_id: str) -> bool:
        if any(ans.playerId == player_id for ans in self.player_answers):
            return False
        player = next((p for p in self.players if p.id == player_id), None)
        if not player:
            return False
        hand = self.player_cards.get(player_id, [])
        chosen_card = next((c for c in hand if c.id == card_id), None)
        if not chosen_card:
            return False
        answer = PlayerAnswer(playerId=player_id, nickname=player.nickname, card=chosen_card)
        self.player_answers.append(answer)
        self.player_cards[player_id] = [c for c in hand if c.id != card_id]
        self.used_white_cards.append(chosen_card)
        if len(self.player_answers) >= len(self.players) and self.game_phase == "selection":
            self.cancel_timer()
            asyncio.create_task(self._transition_to_presentation())
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def submit_vote(self, voter_id: str, voted_player_id: str) -> bool:
        self.votes[voter_id] = voted_player_id
        if len(self.votes) == len(self.players) and self.game_phase == "voting":
            self.cancel_timer()
            self.tally_votes()
            self.next_round()
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def tally_votes(self):
        vote_counts = {}
        for voted in self.votes.values():
            vote_counts[voted] = vote_counts.get(voted, 0) + 1
        if not vote_counts:
            return []
        max_votes = max(vote_counts.values())
        winners = [pid for pid, count in vote_counts.items() if count == max_votes]
        for winner_id in winners:
            winner = next((p for p in self.players if p.id == winner_id), None)
            if winner:
                winner.score += 1
        return winners

    async def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start")
        if not self.black_cards or not self.white_cards:
            await self.load_cards()
        self.current_round = 0
        self.game_phase = "selection"
        self.player_answers.clear()
        self.votes.clear()
        self.round_winners.clear()
        self.deal_cards()
        self.select_black_card()
        self.timer_value = self.settings.selectionTime
        self.timer_task = asyncio.create_task(self._run_selection_timer())
        if self.notify:
            await self.notify()

    async def _run_selection_timer(self):
        while self.timer_value > 0 and self.game_phase == "selection":
            await asyncio.sleep(1)
            self.timer_value -= 1
            if self.notify:
                await self.notify()
        if self.game_phase == "selection":
            for player in self.players:
                if not any(ans.playerId == player.id for ans in self.player_answers):
                    hand = self.player_cards.get(player.id, [])
                    if hand:
                        self.submit_answer(player.id, random.choice(hand).id)
            await self._transition_to_presentation()

    async def _transition_to_presentation(self):
        self.game_phase = "presentation"
        self.cancel_timer()
        if self.notify:
            await self.notify()
        await asyncio.sleep(5)
        await self._transition_to_voting()

    async def _transition_to_voting(self):
        self.game_phase = "voting"
        self.timer_value = self.settings.votingTime
        if self.notify:
            await self.notify()
        self.timer_task = asyncio.create_task(self._run_voting_timer())

    async def _run_voting_timer(self):
        while self.timer_value > 0 and self.game_phase == "voting":
            await asyncio.sleep(1)
            self.timer_value -= 1
            if self.notify:
                await self.notify()
        if self.game_phase == "voting":
            self.tally_votes()
            self.next_round()

    def next_round(self):
        self.player_answers.clear()
        self.votes.clear()
        self.current_round += 1
        if any(len(hand) == 0 for hand in self.player_cards.values()):
            self.end_game()
            return False
        self.game_phase = "selection"
        self.timer_value = self.settings.selectionTime
        self.select_black_card()
        self.timer_task = asyncio.create_task(self._run_selection_timer())
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def end_game(self):
        self.game_phase = "results"
        self.players.sort(key=lambda p: p.score, reverse=True)
        self.cancel_timer()

    def cancel_timer(self):
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        if self.presentation_task and not self.presentation_task.done():
            self.presentation_task.cancel()
