import pytest

from app.agent.tools import ALL_TOOLS, get_order_history, save_user_preference, search_products
from app.database import AsyncSessionLocal
from app.services import order_service, product_service, user_service


@pytest.mark.asyncio
async def test_product_service_search_all():
    async with AsyncSessionLocal() as session:
        products = await product_service.search_products(session=session, limit=50)
        assert len(products) >= 40


@pytest.mark.asyncio
async def test_product_service_search_organic_filter():
    async with AsyncSessionLocal() as session:
        # Search organic honey under $20
        results = await product_service.search_products(
            session=session,
            query="honey",
            is_organic=True,
            max_price=20.0,
        )
        assert len(results) >= 1
        for p in results:
            assert p["is_organic"] is True
            assert float(p["price"]) <= 20.0
            assert "honey" in p["name"].lower() or "honey" in p["description"].lower()


@pytest.mark.asyncio
async def test_order_service_history():
    async with AsyncSessionLocal() as session:
        orders = await order_service.get_order_history(session=session, user_id=1)
        assert len(orders) >= 1
        assert orders[0]["user_id"] == 1
        assert "items" in orders[0]
        assert len(orders[0]["items"]) > 0


@pytest.mark.asyncio
async def test_user_preference_service():
    async with AsyncSessionLocal() as session:
        pref = await user_service.get_user_preference(session=session, user_id=1)
        assert pref is not None
        assert pref["user_id"] == 1
        assert pref["prefers_organic"] is True

        # Test updating preference
        updated = await user_service.save_user_preference(
            session=session,
            user_id=1,
            max_price_limit=25.0,
            notes="Updated notes via test",
        )
        assert updated["max_price_limit"] == 25.0
        assert updated["notes"] == "Updated notes via test"

        # Revert back to 20.0
        await user_service.save_user_preference(
            session=session,
            user_id=1,
            max_price_limit=20.0,
            notes="User Alex prefers organic items and has a $20 max price limit per item.",
        )


@pytest.mark.asyncio
async def test_langchain_tool_search_products():
    # Invoke search_products tool via .ainvoke
    output = await search_products.ainvoke({
        "query": "honey",
        "is_organic": True,
        "max_price": 20.0,
    })
    assert "Organic Raw Wildflower Honey" in output
    assert "$14.99" in output
    # Make sure $35 Manuka honey was filtered out because max_price=20
    assert "Premium Imported Manuka Honey" not in output


@pytest.mark.asyncio
async def test_langchain_tool_order_history():
    output = await get_order_history.ainvoke({"user_id": 1})
    assert "Order history for User ID 1" in output
    assert "Order #" in output


@pytest.mark.asyncio
async def test_langchain_tool_save_preference():
    output = await save_user_preference.ainvoke({
        "user_id": 99,
        "prefers_organic": True,
        "max_price_limit": 15.0,
        "notes": "Testing preferences",
    })
    assert "Successfully updated preferences for User ID 99" in output
    assert "Organic Preferred: True" in output
    assert "$15.00" in output


def test_all_tools_list():
    assert len(ALL_TOOLS) == 3
    tool_names = [t.name for t in ALL_TOOLS]
    assert "search_products" in tool_names
    assert "get_order_history" in tool_names
    assert "save_user_preference" in tool_names
