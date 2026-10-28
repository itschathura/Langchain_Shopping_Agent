import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.order import Order
from app.models.product import Product
from app.models.user_preference import UserPreference

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        # Seed test items
        p1 = Product(
            name="Organic Raw Wildflower Honey",
            description="Pure raw organic honey.",
            category="Honey & Sweeteners",
            price=14.99,
            is_organic=True,
            stock=45,
        )
        p2 = Product(
            name="Standard Clover Honey",
            description="Everyday clover honey.",
            category="Honey & Sweeteners",
            price=6.99,
            is_organic=False,
            stock=80,
        )
        p3 = Product(
            name="Premium Manuka Honey MGO 400+",
            description="Authentic New Zealand Manuka honey.",
            category="Honey & Sweeteners",
            price=35.00,
            is_organic=True,
            stock=15,
        )
        p4 = Product(
            name="Organic Rolled Oats",
            description="Gluten-free organic rolled oats.",
            category="Pantry & Grains",
            price=4.50,
            is_organic=True,
            stock=100,
        )
        session.add_all([p1, p2, p3, p4])

        # Seed user preference for user 1
        pref1 = UserPreference(
            user_id=1,
            prefers_organic=True,
            max_price_limit=20.00,
            notes="Prefers organic items under $20.",
        )
        session.add(pref1)

        # Seed past order for user 1
        order1 = Order(
            user_id=1,
            items=[{"product_id": 1, "name": "Organic Raw Wildflower Honey", "price": 14.99, "quantity": 1}],
            total_amount=14.99,
            status="completed",
        )
        session.add(order1)

        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

