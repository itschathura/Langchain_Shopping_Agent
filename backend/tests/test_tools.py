import json
import pytest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools import (
    AGENT_TOOLS,
    get_order_history,
    save_user_preference,
    search_products,
)
from tests.conftest import TestAsyncSessionLocal


def test_agent_tools_registration():
    """Verify all 3 required tools are registered with schemas."""
    tool_names = [t.name for t in AGENT_TOOLS]
    assert "search_products" in tool_names
    assert "get_order_history" in tool_names
    assert "save_user_preference" in tool_names

    for t in AGENT_TOOLS:
        assert t.args_schema is not None
        assert t.description != ""


@pytest.mark.asyncio
async def test_tool_search_products(db_session: AsyncSession):
    """Test calling the search_products LangChain tool."""
    with patch("app.agent.tools.AsyncSessionLocal", TestAsyncSessionLocal):
        result_json_str = await search_products.ainvoke({
            "query": "honey",
            "is_organic": True,
            "max_price": 20.0,
        })
        results = json.loads(result_json_str)
        assert len(results) == 1
        assert results[0]["name"] == "Organic Raw Wildflower Honey"
        assert results[0]["price"] == 14.99


@pytest.mark.asyncio
async def test_tool_search_products_no_match(db_session: AsyncSession):
    """Test calling search_products with parameters that match nothing."""
    with patch("app.agent.tools.AsyncSessionLocal", TestAsyncSessionLocal):
        result_str = await search_products.ainvoke({
            "query": "nonexistent_item_xyz",
        })
        assert "No products found matching criteria" in result_str


@pytest.mark.asyncio
async def test_tool_get_order_history(db_session: AsyncSession):
    """Test calling the get_order_history LangChain tool."""
    with patch("app.agent.tools.AsyncSessionLocal", TestAsyncSessionLocal):
        result_json_str = await get_order_history.ainvoke({"user_id": 1})
        orders = json.loads(result_json_str)
        assert len(orders) == 1
        assert orders[0]["user_id"] == 1
        assert orders[0]["total_amount"] == 14.99


@pytest.mark.asyncio
async def test_tool_save_user_preference(db_session: AsyncSession):
    """Test calling the save_user_preference LangChain tool."""
    with patch("app.agent.tools.AsyncSessionLocal", TestAsyncSessionLocal):
        result_str = await save_user_preference.ainvoke({
            "user_id": 1,
            "prefers_organic": True,
            "max_price_limit": 18.50,
            "notes": "Updated budget",
        })
        assert "Preferences successfully updated for user 1" in result_str
        assert "18.5" in result_str

