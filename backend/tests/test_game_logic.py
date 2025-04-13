import pytest
from app.api.game.logic import Game
from app.api.db.models import WhiteCard, BlackCard, PlayerAnswer
import asyncio


def test_add_and_remove_player():
    game = Game(game_id="abc123", host_id="host")
    player = game.add_player("p1", "Alice")

    assert len(game.players) == 1
    assert player.nickname == "Alice"

    game.remove_player("p1")
    assert len(game.players) == 0


def test_deal_cards():
    game = Game(game_id="abc123", host_id="host")
    game.add_player("p1", "Alice")
    game.white_cards = [WhiteCard(id=str(i), content=f"Card {i}") for i in range(10)]

    game.settings.cardsPerPlayer = 5
    game.deal_cards()

    hand = game.player_cards["p1"]
    assert len(hand) == 5
    assert all(isinstance(card, WhiteCard) for card in hand)


def test_select_black_card():
    game = Game(game_id="abc123", host_id="host")
    game.black_cards = [BlackCard(id="b1", content="Black question")]

    game.select_black_card()
    assert game.current_black_card is not None
    assert game.current_black_card.id == "b1"


def test_submit_answer():
    game = Game(game_id="abc123", host_id="host")
    game.add_player("p1", "Alice")

    card = WhiteCard(id="c1", content="Funny")
    game.player_cards["p1"] = [card]
    game.settings.cardsPerPlayer = 1

    result = game.submit_answer("p1", "c1")
    assert result is True
    assert len(game.player_answers) == 1
    assert isinstance(game.player_answers[0], PlayerAnswer)


def test_tally_votes():
    game = Game(game_id="abc123", host_id="host")
    game.add_player("p1", "Alice")
    game.add_player("p2", "Bob")

    game.votes = {
        "p1": "p2",
        "p2": "p2"
    }

    winners = game.tally_votes()
    assert winners == ["p2"]

    bob = next(p for p in game.players if p.id == "p2")
    assert bob.score == 1

@pytest.mark.asyncio
async def test_next_round_starts_over():
    game = Game(game_id="abc123", host_id="host")
    game.add_player("p1", "Alice")
    game.add_player("p2", "Bob")
    game.white_cards = [WhiteCard(id=str(i), content=f"White {i}") for i in range(20)]
    game.black_cards = [BlackCard(id="b1", content="Question?")]

    game.deal_cards()
    game.select_black_card()

    card1 = game.player_cards["p1"][0]
    card2 = game.player_cards["p2"][0]
    game.submit_answer("p1", card1.id)
    game.submit_answer("p2", card2.id)

    game.votes = {"p1": "p2", "p2": "p2"}
    game.tally_votes()

    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    result = game.next_round()

    await asyncio.sleep(0.1)

    assert result is True
    assert game.current_round == 1
    assert game.game_phase == "selection"
