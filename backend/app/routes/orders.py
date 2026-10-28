from typing import Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Orders"])


class CreateOrderRequest(BaseModel):
    user_id: int
    items: list[dict[str, Any]] = Field(..., description="List of items with product_id, name, price, quantity")
    total_amount: float = Field(..., ge=0.0)


@router.get("/{user_id}", response_model=list[dict[str, Any]])
async def get_orders_by_user(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve past order history receipts for a given user ID."""
    return await order_service.get_order_history(
        session=db,
        user_id=user_id,
        limit=limit,
    )


@router.post("", response_model=dict[str, Any], status_code=201)
async def create_new_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new checkout order receipt."""
    return await order_service.create_order(
        session=db,
        user_id=request.user_id,
        items=request.items,
        total_amount=request.total_amount,
    )

