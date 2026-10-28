from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preference import UserPreference


async def get_user_preference(session: AsyncSession, user_id: int) -> dict | None:
    """
    Fetch the shopping preferences for a specific user.

    Args:
        session: Active SQLAlchemy async session.
        user_id: Unique user identifier.

    Returns:
        Dictionary of user preferences or None if no preferences saved yet.
    """
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    result = await session.execute(stmt)
    pref = result.scalar_one_or_none()
    return pref.to_dict() if pref else None


async def save_user_preference(
    session: AsyncSession,
    user_id: int,
    prefers_organic: bool | None = None,
    max_price_limit: float | None = None,
    notes: str | None = None,
) -> dict:
    """
    Upsert (create or update) shopping preferences for a specific user.

    Args:
        session: Active SQLAlchemy async session.
        user_id: Unique user identifier.
        prefers_organic: Optional boolean flag whether user prefers organic products.
        max_price_limit: Optional upper price limit per product.
        notes: Optional custom notes or dietary guidelines (e.g. "Lactose-free, hates peanuts").

    Returns:
        Updated user preference dictionary.
    """
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    result = await session.execute(stmt)
    pref = result.scalar_one_or_none()

    if pref is None:
        pref = UserPreference(
            user_id=user_id,
            prefers_organic=prefers_organic if prefers_organic is not None else False,
            max_price_limit=max_price_limit,
            notes=notes,
        )
        session.add(pref)
    else:
        if prefers_organic is not None:
            pref.prefers_organic = prefers_organic
        if max_price_limit is not None:
            pref.max_price_limit = max_price_limit
        if notes is not None:
            pref.notes = notes

    await session.commit()
    await session.refresh(pref)
    return pref.to_dict()
