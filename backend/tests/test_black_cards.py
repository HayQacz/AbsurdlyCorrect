import pytest


@pytest.mark.asyncio
async def test_create_get_delete_black_card(test_client):
    # --- CREATE ---
    card_data = {"content": "Test black card content"}
    create_response = await test_client.post("/black_cards", json=card_data)
    assert create_response.status_code == 200

    created_card = create_response.json()
    card_id = created_card["id"]

    # --- GET ---
    get_response = await test_client.get("/black_cards")
    assert get_response.status_code == 200
    assert any(card["id"] == card_id for card in get_response.json())

    # --- DELETE ---
    delete_response = await test_client.delete(f"/black_cards/{card_id}")
    assert delete_response.status_code == 200

    # --- GET after DELETE ---
    get_after = await test_client.get("/black_cards")
    assert all(card["id"] != card_id for card in get_after.json())
