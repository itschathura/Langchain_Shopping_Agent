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
) -> list[dict]:
    """
    Search the product catalog with multi-field filtering.

    Args:
        session: Active SQLAlchemy async session.
        query: Optional search keyword matching product name or description.
        is_organic: Filter strictly by organic certification (True/False).
        max_price: Upper price limit cap.
        category: Specific category name or partial match.
        limit: Maximum number of products to return (default 10).

    Returns:
        List of product dictionaries.
    """
    stmt = select(Product)

    if query and query.strip():
        term = f"%{query.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(term), Product.description.ilike(term)))

    if is_organic is not None:
        stmt = stmt.where(Product.is_organic == is_organic)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    if category and category.strip():
        stmt = stmt.where(Product.category.ilike(f"%{category.strip()}%"))

    # Order by price ascending to prioritize budget-friendly options
    stmt = stmt.order_by(Product.price.asc()).limit(limit)

    result = await session.execute(stmt)
    products = result.scalars().all()
    return [p.to_dict() for p in products]


async def get_product_by_id(session: AsyncSession, product_id: int) -> dict | None:
    """Fetch a single product by its unique primary key ID."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    return product.to_dict() if product else None


async def get_all_categories(session: AsyncSession) -> list[str]:
    """Retrieve all distinct product categories currently available."""
    stmt = select(Product.category).distinct().order_by(Product.category.asc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
