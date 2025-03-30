import uuid
import random
import asyncio
from typing import List, Dict, Optional, Callable, Awaitable
from fastapi import WebSocket

from app.models import (
    BlackCard,
    WhiteCard,
    Player,
    PlayerAnswer,
    GameSettings,
)
from app.models import BlackCardDB, WhiteCardDB
from sqlalchemy import select
from app.database import async_session

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

    def add_player(self, player_id: str, nickname: str) -> Player:
        print(f"DEBUG: add_player -> player_id={player_id}, nickname={nickname}, game_id={self.id}")
        for existing in self.players:
            if existing.id == player_id:
                print("DEBUG: add_player -> player already in game.")
                return existing
        if len(self.players) >= self.settings.maxPlayers:
            raise ValueError("Game is full")
        for pl in self.players:
            if pl.nickname == nickname:
                suffix = str(random.randint(1, 999))
                nickname = f"{nickname}_{suffix}"
                break
        p = Player(id=player_id, nickname=nickname)
        self.players.append(p)
        return p

    def remove_player(self, player_id: str):
        print(f"DEBUG: remove_player -> {player_id} from game {self.id}")
        self.players = [p for p in self.players if p.id != player_id]
        if player_id in self.connections:
            del self.connections[player_id]
        if player_id == self.host_id and self.players:
            self.host_id = self.players[0].id
        if len(self.players) < 2 and self.game_phase != "lobby":
            self.end_game()

    async def load_cards(self):
        print("DEBUG: load_cards -> ładowanie kart z bazy danych")
        async with async_session() as session:
            result = await session.execute(select(BlackCardDB))
            db_black_cards = result.scalars().all()
            self.black_cards = [BlackCard.from_orm(card) for card in db_black_cards]
            result = await session.execute(select(WhiteCardDB))
            db_white_cards = result.scalars().all()
            self.white_cards = [WhiteCard.from_orm(card) for card in db_white_cards]
        random.shuffle(self.black_cards)
        random.shuffle(self.white_cards)

    async def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start")
        print(f"DEBUG: start_game -> game {self.id} with {len(self.players)} players")
        if not self.black_cards and not self.white_cards:
            await self.load_cards()
        self.current_round = 0
        self.game_phase = "selection"
        self.player_answers.clear()
        self.votes.clear()
        self.round_winners.clear()
        self.timer_value = self.settings.selectionTime
        self.timer_task = asyncio.create_task(self._run_selection_timer())
        self.deal_cards()
        self.select_black_card()
        if self.notify:
            await self.notify()

    async def _run_selection_timer(self):
        while self.timer_value > 0 and self.game_phase == "selection":
            await asyncio.sleep(1)
            self.timer_value -= 1
            print(f"DEBUG: Selection Timer updated, timeLeft: {self.timer_value}")
            if self.notify:
                await self.notify()
        if self.game_phase == "selection":
            for p in self.players:
                if not any(ans.playerId == p.id for ans in self.player_answers):
                    hand = self.player_cards.get(p.id, [])
                    if hand:
                        chosen = random.choice(hand)
                        print(f"DEBUG: Auto-selecting answer for player {p.id}")
                        self.submit_answer(p.id, chosen.id)
            await self._transition_to_presentation()

    async def _transition_to_presentation(self):
        print("DEBUG: transitioning to presentation phase")
        self.game_phase = "presentation"
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        if self.notify:
            await self.notify()
        await asyncio.sleep(5)
        await self._transition_to_voting()

    async def _transition_to_voting(self):
        print("DEBUG: transitioning to voting phase")
        self.game_phase = "voting"
        self.timer_value = self.settings.votingTime
        if self.notify:
            await self.notify()
        self.timer_task = asyncio.create_task(self._run_voting_timer())

    async def _run_voting_timer(self):
        while self.timer_value > 0 and self.game_phase == "voting":
            await asyncio.sleep(1)
            self.timer_value -= 1
            print(f"DEBUG: Voting Timer updated, timeLeft: {self.timer_value}")
            if self.notify:
                await self.notify()
            if len(self.votes) == len(self.players):
                if self.timer_task and not self.timer_task.done():
                    self.timer_task.cancel()
                break
        if self.game_phase == "voting":
            self.tally_votes()
            self.next_round()

    def deal_cards(self):
        print(f"DEBUG: deal_cards -> {self.settings.cardsPerPlayer} kart dla graczy, gra {self.id}")
        for player in self.players:
            if len(self.white_cards) < self.settings.cardsPerPlayer:
                print("DEBUG: zabrakło kart białych, tasujemy użyte karty")
                self.white_cards.extend(self.used_white_cards)
                self.used_white_cards.clear()
                random.shuffle(self.white_cards)
            new_hand: List[WhiteCard] = []
            for _ in range(self.settings.cardsPerPlayer):
                if self.white_cards:
                    c = self.white_cards.pop(0)
                    new_hand.append(c)
            self.player_cards[player.id] = new_hand

    def select_black_card(self):
        if not self.black_cards:
            self.black_cards.extend(self.used_black_cards)
            self.used_black_cards.clear()
            random.shuffle(self.black_cards)
        if self.black_cards:
            self.current_black_card = self.black_cards.pop(0)
            self.used_black_cards.append(self.current_black_card)
            print(f"DEBUG: select_black_card -> game {self.id}, blackCard={self.current_black_card.content}")

    def submit_answer(self, player_id: str, card_id: str) -> bool:
        print(f"DEBUG: submit_answer -> player={player_id}, card_id={card_id}, game={self.id}")
        if any(ans.playerId == player_id for ans in self.player_answers):
            return False
        pl = next((p for p in self.players if p.id == player_id), None)
        if not pl:
            return False
        hand = self.player_cards.get(player_id, [])
        chosen_card = next((c for c in hand if c.id == card_id), None)
        if not chosen_card:
            return False
        ans = PlayerAnswer(playerId=player_id, nickname=pl.nickname, card=chosen_card)
        self.player_answers.append(ans)
        self.player_cards[player_id] = [c for c in hand if c.id != card_id]
        self.used_white_cards.append(chosen_card)
        if len(self.player_answers) >= len(self.players) and self.game_phase == "selection":
            if self.timer_task and not self.timer_task.done():
                self.timer_task.cancel()
            asyncio.create_task(self._transition_to_presentation())
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def submit_vote(self, voter_id: str, voted_player_id: str) -> bool:
        print(f"DEBUG: submit_vote -> voter={voter_id}, voted={voted_player_id}, game={self.id}")
        voter = next((p for p in self.players if p.id == voter_id), None)
        if not voter:
            return False
        voted_pl = next((p for p in self.players if p.id == voted_player_id), None)
        voted_ans = next((a for a in self.player_answers if a.playerId == voted_player_id), None)
        if not voted_pl or not voted_ans:
            return False
        self.votes[voter_id] = voted_player_id
        if len(self.votes) == len(self.players) and self.game_phase == "voting":
            if self.timer_task and not self.timer_task.done():
                self.timer_task.cancel()
            self.tally_votes()
            self.next_round()
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def tally_votes(self):
        print(f"DEBUG: tally_votes -> game={self.id}, votes={self.votes}")
        vote_counts: Dict[str, int] = {}
        for vpid in self.votes.values():
            vote_counts[vpid] = vote_counts.get(vpid, 0) + 1
        if not vote_counts:
            return []
        max_votes = max(vote_counts.values())
        winners = [pid for pid, cnt in vote_counts.items() if cnt == max_votes]
        for w in winners:
            pl = next((p for p in self.players if p.id == w), None)
            if pl:
                pl.score += 1
        return winners

    def next_round(self):
        print(f"DEBUG: next_round -> game={self.id}")
        self.player_answers.clear()
        self.votes.clear()
        self.current_round += 1
        # Jeśli któryś gracz nie ma już kart, kończymy grę
        for pid, hand in self.player_cards.items():
            if not hand:
                self.end_game()
                return False
        self.game_phase = "selection"
        self.timer_value = self.settings.selectionTime
        self.timer_task = asyncio.create_task(self._run_selection_timer())
        self.select_black_card()
        if self.notify:
            asyncio.create_task(self.notify())
        return True

    def end_game(self):
        print(f"DEBUG: end_game -> game={self.id}")
        self.game_phase = "results"
        self.players.sort(key=lambda x: x.score, reverse=True)
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        if self.presentation_task and not self.presentation_task.done():
            self.presentation_task.cancel()
