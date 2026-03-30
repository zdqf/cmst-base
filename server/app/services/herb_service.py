"""Herb service layer — business logic for herb queries.

Requirements:
- 2.2: Daily herb selection
- 3.2: Category browsing
- 3.3: Keyword search
- 3.4: Paginated query, max 20 per page
- 3.5: Detail query
- 3.6: Content is informational only
"""

import hashlib
import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.herb import Herb
from app.schemas.common import PaginatedResponse
from app.schemas.herb import HerbListItem, HerbSearchParams


async def list_herbs(
    db: AsyncSession, params: HerbSearchParams
) -> PaginatedResponse[HerbListItem]:
    """Paginated herb list with optional category filter and keyword search.

    Only returns active herbs. Supports ILIKE keyword search on name.
    """
    base_filter = Herb.status == "active"

    # Build query conditions
    conditions = [base_filter]
    if params.category:
        conditions.append(Herb.category == params.category)
    if params.keyword:
        conditions.append(Herb.name.ilike(f"%{params.keyword}%"))

    # Count total
    count_stmt = select(func.count()).select_from(Herb).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch page
    offset = (params.page - 1) * params.page_size
    query_stmt = (
        select(Herb)
        .where(*conditions)
        .order_by(Herb.name)
        .offset(offset)
        .limit(params.page_size)
    )
    result = await db.execute(query_stmt)
    herbs = result.scalars().all()

    items = [HerbListItem.model_validate(h) for h in herbs]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


async def get_herb_detail(db: AsyncSession, herb_id: uuid.UUID) -> Herb | None:
    """Get a single herb by ID."""
    stmt = select(Herb).where(Herb.id == herb_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_daily_herb(db: AsyncSession) -> Herb | None:
    """Select one herb as today's recommendation.

    Uses a date-based hash to consistently pick the same herb for a given day.
    Requirement 2.2: 每日从 Herb_Database 中选取一味中药作为今日草本推荐
    """
    # Count active herbs
    count_stmt = select(func.count()).select_from(Herb).where(Herb.status == "active")
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    if total == 0:
        return None

    # Deterministic index from today's date
    today_str = date.today().isoformat()
    hash_val = int(hashlib.md5(today_str.encode()).hexdigest(), 16)
    index = hash_val % total

    stmt = (
        select(Herb)
        .where(Herb.status == "active")
        .order_by(Herb.id)
        .offset(index)
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
