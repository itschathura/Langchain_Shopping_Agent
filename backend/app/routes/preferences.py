from typing import Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["User Preferences"])


class UpdatePreferencesRequest(BaseModel):
    prefers_organic: Optional[bool] = Field(None, description="Set default organic preference")
    max_price_limit: Optional[float] = Field(None, ge=0.0, description="Max budget cap per product in USD")
    notes: Optional[str] = Field(None, description="Dietary notes, allergies, or shopping habits")


@router.get("/{user_id}/preferences", response_model=dict[str, Any])
async def get_preferences(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve saved preferences for a given user."""
    pref = await user_service.get_user_preference(session=db, user_id=user_id)
    if not pref:
        return {
            "id": None,
            "user_id": user_id,
            "prefers_organic": False,
            "max_price_limit": None,
            "notes": None,
        }
    return pref


@router.post("/{user_id}/preferences", response_model=dict[str, Any])
async def update_preferences(
    user_id: int,
    request: UpdatePreferencesRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create or update preferences for a given user."""
    return await user_service.save_user_preference(
        session=db,
        user_id=user_id,
        prefers_organic=request.prefers_organic,
        max_price_limit=request.max_price_limit,
        notes=request.notes,
    )

