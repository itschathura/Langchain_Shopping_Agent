from typing import Any
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


async def search_products(
    session: AsyncSession,
    query: str | None = None,
    is_organic: bool | None = None,
    max_price: float | None = None,
    category: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search and filter products based on query keywords, organic status, max price, and category."""
    stmt = select(Product)

    # Keyword search across name and description
    if query and query.strip():
        search_terms = query.strip().split()
        for term in search_terms:
            pattern = f"%{term}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )

    # Filter by organic preference
    if is_organic is not None:
        stmt = stmt.where(Product.is_organic == is_organic)

    # Filter by maximum price limit
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # Filter by category
    if category and category.strip():
        stmt = stmt.where(Product.category.ilike(f"%{category.strip()}%"))

    # Order by price ascending and limit
    stmt = stmt.order_by(Product.price.asc()).limit(limit)

    result = await session.execute(stmt)
    products = result.scalars().all()
    return [p.to_dict() for p in products]


async def get_product_by_id(
    session: AsyncSession,
    product_id: int,
) -> dict[str, Any] | None:
    """Retrieve a single product by its unique database ID."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    return product.to_dict() if product else None


async def get_all_products(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all catalog products with pagination and optional category filter."""
    stmt = select(Product)
    if category and category.strip():
        stmt = stmt.where(Product.category.ilike(f"%{category.strip()}%"))

    stmt = stmt.order_by(Product.id.asc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return [p.to_dict() for p in products]
