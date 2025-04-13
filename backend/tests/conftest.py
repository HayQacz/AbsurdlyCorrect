import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from app.main import app

@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
