from langchain_core.tools import tool

from app.database import AsyncSessionLocal
from app.services import order_service, product_service, user_service


@tool
async def search_products(
    query: str = "",
    category: str | None = None,
    is_organic: bool | None = None,
    max_price: float | None = None,
    limit: int = 8,
) -> str:
    """Search the store product catalog for groceries, pantry staples, and items.

    Args:
        query: Keywords to search in product title or description (e.g. 'honey', 'oats', 'milk', 'crackers').
        category: Filter by specific category (e.g. 'Honey & Sweeteners', 'Pantry & Grains', 'Dairy & Alternatives', 'Produce', 'Snacks', 'Beverages', 'Bakery', 'Oils & Condiments').
        is_organic: Set to True if the customer specifically wants organic certified products, False for conventional, or omit if not specified.
        max_price: Maximum price per unit in USD (e.g. 20.0 for items <= $20.00).
        limit: Max number of products to return (default 8).

    Returns:
        A formatted list of products with ID, name, price, organic status, and stock.
    """
    try:
        async with AsyncSessionLocal() as session:
            products = await product_service.search_products(
                session=session,
                query=query if query.strip() else None,
                is_organic=is_organic,
                max_price=max_price,
                category=category,
                limit=limit,
            )

        if not products:
            criteria = []
            if query:
                criteria.append(f"query='{query}'")
            if category:
                criteria.append(f"category='{category}'")
            if is_organic is not None:
                criteria.append(f"organic={is_organic}")
            if max_price is not None:
                criteria.append(f"max_price=${max_price:.2f}")

            crit_str = ", ".join(criteria) if criteria else "given filters"
            return f"No products found matching the criteria ({crit_str}). Please suggest related categories or adjust price/filters."

        lines = [f"Found {len(products)} product(s):"]
        for p in products:
            org_tag = "Organic" if p.get("is_organic") else "Conventional"
            lines.append(
                f"- [ID: {p['id']}] {p['name']} | Price: ${p['price']:.2f} | "
                f"Category: {p['category']} | Status: {org_tag} | Stock: {p['stock']} | "
                f"Description: {p.get('description', 'N/A')}"
            )
        return "\n".join(lines)
    except Exception as exc:  # noqa: BLE001
        return f"Error executing product search: {exc!s}"


@tool
async def get_order_history(
    user_id: int,
    limit: int = 5,
) -> str:
    """Retrieve past purchase receipts and order history for a specific customer.

    Args:
        user_id: The unique ID number of the customer (e.g. 1 for Alex).
        limit: Maximum number of previous orders to return (default 5, latest first).

    Returns:
        Formatted summary of past orders with dates, items bought, quantities, and totals.
    """
    try:
        async with AsyncSessionLocal() as session:
            orders = await order_service.get_order_history(
                session=session,
                user_id=user_id,
                limit=limit,
            )

        if not orders:
            return f"No past orders found for User ID {user_id}."

        lines = [f"Order history for User ID {user_id} ({len(orders)} order(s) found):"]
        for o in orders:
            date_str = o.get("created_at", "Unknown date")[:10] if o.get("created_at") else "Unknown"
            lines.append(f"\nOrder #{o['id']} (Date: {date_str}, Status: {o['status']}, Total: ${o['total_amount']:.2f}):")
            for item in o.get("items", []):
                lines.append(
                    f"  * {item.get('name', 'Item')} x{item.get('quantity', 1)} @ ${item.get('price', 0.0):.2f}"
                )
        return "\n".join(lines)
    except Exception as exc:  # noqa: BLE001
        return f"Error retrieving order history: {exc!s}"


@tool
async def save_user_preference(
    user_id: int,
    prefers_organic: bool | None = None,
    max_price_limit: float | None = None,
    notes: str | None = None,
) -> str:
    """Save or update persistent shopping preferences for a customer.

    Use this when the customer expresses preferences like preferring organic foods,
    having a strict budget cap per item, or having dietary guidelines.

    Args:
        user_id: The customer's unique ID number.
        prefers_organic: True if the user wants organic items prioritized, False otherwise.
        max_price_limit: Upper price ceiling per product (e.g. 20.0 for $20.00).
        notes: Dietary notes or special instructions (e.g. 'Gluten-free snacks only').

    Returns:
        Confirmation message with the updated preferences.
    """
    try:
        async with AsyncSessionLocal() as session:
            updated = await user_service.save_user_preference(
                session=session,
                user_id=user_id,
                prefers_organic=prefers_organic,
                max_price_limit=max_price_limit,
                notes=notes,
            )

        price_str = (
            f"${updated['max_price_limit']:.2f}"
            if updated.get("max_price_limit") is not None
            else "None"
        )
        return (
            f"Successfully updated preferences for User ID {user_id}:\n"
            f"- Organic Preferred: {updated.get('prefers_organic')}\n"
            f"- Max Price Limit: {price_str}\n"
            f"- Notes: {updated.get('notes') or 'None'}"
        )
    except Exception as exc:  # noqa: BLE001
        return f"Error saving preferences: {exc!s}"


ALL_TOOLS = [
    search_products,
    get_order_history,
    save_user_preference,
]
