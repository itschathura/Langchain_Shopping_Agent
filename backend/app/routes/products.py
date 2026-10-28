from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=list[dict[str, Any]])
async def list_products(
    query: Optional[str] = Query(None, description="Search term in product name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_organic: Optional[bool] = Query(None, description="Filter organic items"),
    max_price: Optional[float] = Query(None, ge=0.0, description="Max item price cap"),
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve catalog products with optional keyword and attribute filters."""
    if query or is_organic is not None or max_price is not None:
        return await product_service.search_products(
            session=db,
            query=query,
            is_organic=is_organic,
            max_price=max_price,
            category=category,
            limit=limit,
        )

    return await product_service.get_all_products(
        session=db,
        skip=skip,
        limit=limit,
        category=category,
    )


@router.get("/{product_id}", response_model=dict[str, Any])
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single product by ID."""
    product = await product_service.get_product_by_id(session=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    return product

