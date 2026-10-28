from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


async def get_order_history(
    session: AsyncSession,
    user_id: int,
    limit: int = 5,
) -> list[dict]:
    """
    Retrieve previous order receipts for a specific user.

    Args:
        session: Active SQLAlchemy async session.
        user_id: Unique user identifier.
        limit: Max past orders to retrieve (default 5, ordered most recent first).

    Returns:
        List of order dictionaries containing items, total_amount, status, created_at.
    """
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return [order.to_dict() for order in orders]


async def get_order_by_id(session: AsyncSession, order_id: int) -> dict | None:
    """Fetch a specific order by order ID."""
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    return order.to_dict() if order else None
