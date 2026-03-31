"""Payment router — create, callback, and status query endpoints."""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.payment import CreatePaymentRequest, PaymentResponse, PaymentStatusResponse
from app.services.payment_service import (
    create_order_payment,
    handle_payment_notify,
    query_payment_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/create", response_model=ApiResponse)
async def create_payment(
    req: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Create a payment for a pending order. Requires authentication."""
    payment = await create_order_payment(
        db, req.order_id, current_user.id, req.method
    )
    pay_url = None
    if payment.notify_data and isinstance(payment.notify_data, dict):
        pay_url = payment.notify_data.get("pay_url")

    data = PaymentResponse(
        payment_id=payment.id,
        order_id=payment.order_id,
        method=payment.method,
        amount=payment.amount,
        status=payment.status,
        pay_url=pay_url,
        trade_no=payment.trade_no,
        created_at=payment.created_at,
    )
    return ApiResponse(data=data.model_dump(mode="json"))


@router.post("/notify/alipay")
async def alipay_notify(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> str:
    """Alipay async callback endpoint. No authentication required.

    Returns "success" to acknowledge receipt, or "fail" on error.
    """
    form_data = await request.form()
    notify_data = dict(form_data)

    try:
        result = await handle_payment_notify(db, "alipay", notify_data)
        await db.commit()
        return "success" if result else "fail"
    except Exception:
        logger.exception("Error processing Alipay notify")
        return "fail"


@router.post("/notify/wechat")
async def wechat_notify(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """WeChat Pay async callback endpoint. No authentication required.

    Returns {"code": "SUCCESS"} to acknowledge, or {"code": "FAIL"} on error.
    """
    body = await request.body()
    headers = dict(request.headers)

    notify_data = {
        "headers": headers,
        "body": body.decode("utf-8"),
    }

    # WeChat sends JSON body with encrypted resource
    try:
        import json
        json_body = json.loads(body)
        notify_data["resource"] = json_body.get("resource", {})
    except Exception:
        pass

    try:
        result = await handle_payment_notify(db, "wechat", notify_data)
        await db.commit()
        if result:
            return {"code": "SUCCESS", "message": "OK"}
        return {"code": "FAIL", "message": "Processing failed"}
    except Exception:
        logger.exception("Error processing WeChat notify")
        return {"code": "FAIL", "message": "Internal error"}


@router.get("/{payment_id}/status", response_model=ApiResponse)
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Query payment status. Requires authentication.

    If payment is pending, actively queries the provider for latest status.
    Only allows querying own orders' payments.
    """
    import uuid as uuid_mod

    try:
        pid = uuid_mod.UUID(payment_id)
    except ValueError:
        return ApiResponse(code=400, message="Invalid payment ID")

    status_data = await query_payment_status(db, pid, current_user.id)
    return ApiResponse(data=status_data)
