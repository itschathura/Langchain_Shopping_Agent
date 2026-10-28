from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


async def get_order_history(
    session: AsyncSession,
    user_id: int,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve past order history receipts for a given user ID."""
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return [order.to_dict() for order in orders]


async def create_order(
    session: AsyncSession,
    user_id: int,
    items: list[dict[str, Any]],
    total_amount: float,
) -> dict[str, Any]:
    """Create a new order record for a user."""
    order = Order(
        user_id=user_id,
        items=items,
        total_amount=total_amount,
        status="completed",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order.to_dict()
