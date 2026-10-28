import json
from typing import Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import AsyncSessionLocal
from app.services.order_service import get_order_history as svc_get_order_history
from app.services.product_service import search_products as svc_search_products
from app.services.user_service import save_user_preference as svc_save_user_preference


# ==============================================================================
# Pydantic Input Schemas for High Tool-Calling Accuracy
# ==============================================================================

class SearchProductsInput(BaseModel):
    query: Optional[str] = Field(
        default=None,
        description="Search keyword to match in product title or description (e.g., 'honey', 'oats', 'milk', 'crackers', 'coffee'). Use concise terms.",
    )
    is_organic: Optional[bool] = Field(
        default=None,
        description="Set to True to filter strictly for certified organic items, False for conventional non-organic items, or omit/null for any.",
    )
    max_price: Optional[float] = Field(
        default=None,
        description="Maximum item price in USD (e.g. 20.0). Only returns items with price less than or equal to this limit.",
    )
    category: Optional[str] = Field(
        default=None,
        description="Product department/category (e.g. 'Honey & Sweeteners', 'Pantry & Grains', 'Dairy & Alternatives', 'Snacks', 'Beverages', 'Produce', 'Oils & Condiments').",
    )


class GetOrderHistoryInput(BaseModel):
    user_id: int = Field(
        description="The unique integer customer ID whose past orders and receipts are being requested.",
    )
    limit: int = Field(
        default=5,
        description="Maximum number of recent orders to retrieve (default is 5).",
    )


class SaveUserPreferenceInput(BaseModel):
    user_id: int = Field(
        description="The customer's unique integer ID.",
    )
    prefers_organic: Optional[bool] = Field(
        default=None,
        description="Whether the user prefers organic products by default (True or False).",
    )
    max_price_limit: Optional[float] = Field(
        default=None,
        description="Default maximum budget/spending limit per item in USD.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Any specific dietary preferences, allergies, or notes (e.g. 'Gluten-free diet, strict budget under $15').",
    )


# ==============================================================================
# LangChain Tool Implementations
# ==============================================================================

@tool(args_schema=SearchProductsInput)
async def search_products(
    query: Optional[str] = None,
    is_organic: Optional[bool] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
) -> str:
    """Search and filter the store catalog for grocery products, snacks, beverages, and pantry items.
    
    Use this tool whenever the customer:
    - Asks to find, buy, search, or check prices for grocery products
    - Specifies budget constraints (e.g. "under $20")
    - Specifies dietary/organic preferences (e.g. "organic honey")
    - Asks what items are in stock in a particular category
    
    Returns a JSON string containing matched products with id, name, price, organic status, and stock.
    """
    async with AsyncSessionLocal() as session:
        products = await svc_search_products(
            session=session,
            query=query,
            is_organic=is_organic,
            max_price=max_price,
            category=category,
            limit=10,
        )

    if not products:
        filters_applied = []
        if query:
            filters_applied.append(f"query='{query}'")
        if is_organic is not None:
            filters_applied.append(f"is_organic={is_organic}")
        if max_price is not None:
            filters_applied.append(f"max_price=${max_price:.2f}")
        if category:
            filters_applied.append(f"category='{category}'")
        return f"No products found matching criteria ({', '.join(filters_applied)}). Try broadening the search."

    # Return clean, formatted JSON for LLM consumption
    formatted = [
        {
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "is_organic": p["is_organic"],
            "category": p["category"],
            "stock": p["stock"],
            "description": p["description"],
        }
        for p in products
    ]
    return json.dumps(formatted, indent=2)


@tool(args_schema=GetOrderHistoryInput)
async def get_order_history(
    user_id: int,
    limit: int = 5,
) -> str:
    """Retrieve past purchase receipts and order history for a customer.
    
    Use this tool whenever the customer:
    - Asks "What did I order previously?", "What did I buy last week?", or "Show my previous orders"
    - Wants to reorder something they bought in the past
    - Wants to verify past receipt details or purchase totals
    
    Returns a JSON list of past orders with dates, total amounts, and item breakdowns.
    """
    async with AsyncSessionLocal() as session:
        orders = await svc_get_order_history(
            session=session,
            user_id=user_id,
            limit=limit,
        )

    if not orders:
        return f"No prior order history found for user ID {user_id}."

    return json.dumps(orders, indent=2)


@tool(args_schema=SaveUserPreferenceInput)
async def save_user_preference(
    user_id: int,
    prefers_organic: Optional[bool] = None,
    max_price_limit: Optional[float] = None,
    notes: Optional[str] = None,
) -> str:
    """Save or update customer dietary rules, price budget limits, or shopping preferences.
    
    Use this tool whenever the customer says:
    - "Remember that I prefer organic food" or "I only buy organic"
    - "My budget is $15 per item" or "Never show me items over $20"
    - "I am gluten-free" or "I am vegan"
    
    Persists these preferences to the database for future shopping sessions.
    """
    async with AsyncSessionLocal() as session:
        pref = await svc_save_user_preference(
            session=session,
            user_id=user_id,
            prefers_organic=prefers_organic,
            max_price_limit=max_price_limit,
            notes=notes,
        )

    return (
        f"Preferences successfully updated for user {user_id}: "
        f"prefers_organic={pref['prefers_organic']}, "
        f"max_price_limit={pref['max_price_limit']}, "
        f"notes='{pref['notes']}'"
    )


# Export tool catalog list for agent binding
AGENT_TOOLS = [search_products, get_order_history, save_user_preference]
