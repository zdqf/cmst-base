"""Admin dashboard statistics endpoint.

Returns all dashboard counts in a single query to avoid N+1 API calls.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai_diagnosis_log import AIDiagnosisLog
from app.models.consultation import Consultation
from app.models.herb import Herb
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/admin/dashboard", tags=["管理后台-仪表盘"])


@router.get("/stats", response_model=ApiResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Get all dashboard statistics in a single request."""
    users_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    orders_count = (await db.execute(select(func.count(Order.id)))).scalar_one()
    pending_orders = (await db.execute(
        select(func.count(Order.id)).where(Order.status == "pending")
    )).scalar_one()
    consultations_count = (await db.execute(select(func.count(Consultation.id)))).scalar_one()
    pending_consultations = (await db.execute(
        select(func.count(Consultation.id)).where(Consultation.status == "pending")
    )).scalar_one()
    products_count = (await db.execute(select(func.count(Product.id)))).scalar_one()
    herbs_count = (await db.execute(
        select(func.count(Herb.id)).where(Herb.status == "active")
    )).scalar_one()
    diagnosis_count = (await db.execute(select(func.count(AIDiagnosisLog.id)))).scalar_one()

    return ApiResponse(data={
        "users": users_count,
        "orders": orders_count,
        "pending_orders": pending_orders,
        "consultations": consultations_count,
        "pending_consultations": pending_consultations,
        "products": products_count,
        "herbs": herbs_count,
        "diagnosis_logs": diagnosis_count,
    })
