from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preference import UserPreference


async def get_user_preference(
    session: AsyncSession,
    user_id: int,
) -> dict[str, Any] | None:
    """Retrieve saved preferences for a given user ID."""
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
) -> dict[str, Any]:
    """Create or update preferences for a given user ID."""
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    result = await session.execute(stmt)
    pref = result.scalar_one_or_none()

    if pref:
        if prefers_organic is not None:
            pref.prefers_organic = prefers_organic
        if max_price_limit is not None:
            pref.max_price_limit = max_price_limit
        if notes is not None:
            pref.notes = notes
    else:
        pref = UserPreference(
            user_id=user_id,
            prefers_organic=prefers_organic if prefers_organic is not None else False,
            max_price_limit=max_price_limit,
            notes=notes,
        )
        session.add(pref)

    await session.commit()
    await session.refresh(pref)
    return pref.to_dict()
