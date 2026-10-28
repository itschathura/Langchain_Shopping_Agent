import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.order_service import get_order_history
from app.services.product_service import get_product_by_id, search_products
from app.services.user_service import get_user_preference, save_user_preference


@pytest.mark.asyncio
async def test_search_products_all_honey(db_session: AsyncSession):
    products = await search_products(session=db_session, query="honey")
    assert len(products) == 3


@pytest.mark.asyncio
async def test_search_products_organic_filter(db_session: AsyncSession):
    products = await search_products(session=db_session, query="honey", is_organic=True)
    assert len(products) == 2
    assert all(p["is_organic"] for p in products)


@pytest.mark.asyncio
async def test_search_products_price_cap(db_session: AsyncSession):
    # Testing our benchmark constraint: organic honey under $20 cap
    # Wildflower Honey ($14.99) passes, Manuka Honey ($35.00) is filtered out
    products = await search_products(
        session=db_session,
        query="honey",
        is_organic=True,
        max_price=20.00,
    )
    assert len(products) == 1
    assert products[0]["name"] == "Organic Raw Wildflower Honey"
    assert products[0]["price"] == 14.99


@pytest.mark.asyncio
async def test_get_product_by_id(db_session: AsyncSession):
    product = await get_product_by_id(session=db_session, product_id=1)
    assert product is not None
    assert product["name"] == "Organic Raw Wildflower Honey"


@pytest.mark.asyncio
async def test_get_order_history(db_session: AsyncSession):
    orders = await get_order_history(session=db_session, user_id=1)
    assert len(orders) == 1
    assert orders[0]["total_amount"] == 14.99
    assert orders[0]["items"][0]["name"] == "Organic Raw Wildflower Honey"


@pytest.mark.asyncio
async def test_user_preference_crud(db_session: AsyncSession):
    # 1. Fetch existing preference for user 1
    pref = await get_user_preference(session=db_session, user_id=1)
    assert pref is not None
    assert pref["prefers_organic"] is True
    assert pref["max_price_limit"] == 20.00

    # 2. Update user 1 preference
    updated = await save_user_preference(
        session=db_session,
        user_id=1,
        max_price_limit=15.00,
        notes="Budget tightened to $15",
    )
    assert updated["max_price_limit"] == 15.00
    assert updated["notes"] == "Budget tightened to $15"

    # 3. Create preference for new user 99
    new_pref = await save_user_preference(
        session=db_session,
        user_id=99,
        prefers_organic=False,
        max_price_limit=10.00,
    )
    assert new_pref["user_id"] == 99
    assert new_pref["prefers_organic"] is False

