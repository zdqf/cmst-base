"""Payment service with provider abstraction.

Supports Alipay, WeChat Pay, and Mock providers.
Switch via config `payment_provider` without changing business code.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppException, ForbiddenError, NotFoundError
from app.models.order import Order
from app.models.payment import Payment

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------


class BasePaymentProvider(ABC):
    """Abstract base class for payment providers."""

    @abstractmethod
    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> dict:
        """Create a payment with the provider.

        Returns dict with at least: {"pay_url": str, "trade_no": str | None}
        """
        ...

    @abstractmethod
    async def verify_notify(self, data: dict) -> bool:
        """Verify callback signature. Returns True if valid."""
        ...

    @abstractmethod
    async def query_payment(self, trade_no: str) -> dict:
        """Query payment status from provider.

        Returns dict with at least: {"status": str, "trade_no": str}
        """
        ...

    @abstractmethod
    async def refund(self, trade_no: str, amount: Decimal, reason: str) -> dict:
        """Request a refund. Returns dict with refund details."""
        ...


class AlipayProvider(BasePaymentProvider):
    """Alipay payment provider using python-alipay-sdk (RSA2).

    Requires: pip install python-alipay-sdk
    Configure via environment variables:
      ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY, ALIPAY_PUBLIC_KEY,
      ALIPAY_NOTIFY_URL, ALIPAY_RETURN_URL, ALIPAY_SANDBOX
    """

    def __init__(self):
        self.app_id = settings.alipay_app_id
        self.private_key = settings.alipay_private_key
        self.public_key = settings.alipay_public_key
        self.notify_url = settings.alipay_notify_url
        self.return_url = settings.alipay_return_url
        self.sandbox = settings.alipay_sandbox

    def _get_client(self):
        """Lazy-load the Alipay SDK client."""
        from alipay import AliPay

        return AliPay(
            appid=self.app_id,
            app_notify_url=self.notify_url,
            app_private_key_string=self.private_key,
            alipay_public_key_string=self.public_key,
            sign_type="RSA2",
            debug=self.sandbox,
        )

    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> dict:
        try:
            client = self._get_client()
            # WAP pay for mobile web
            order_string = client.api_alipay_trade_wap_pay(
                out_trade_no=order_no,
                total_amount=str(amount),
                subject=subject,
                return_url=self.return_url,
                notify_url=self.notify_url,
            )
            base = (
                "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
                if self.sandbox
                else "https://openapi.alipay.com/gateway.do"
            )
            pay_url = f"{base}?{order_string}"
            logger.info("Alipay payment created for order %s", order_no)
            return {"pay_url": pay_url, "trade_no": None}
        except Exception:
            logger.exception("Alipay create_payment failed for order %s", order_no)
            raise AppException(code=500, message="Payment creation failed")

    async def verify_notify(self, data: dict) -> bool:
        try:
            client = self._get_client()
            sign = data.pop("sign", None)
            sign_type = data.pop("sign_type", None)
            result = client.verify(data, sign)
            # Restore for logging
            if sign:
                data["sign"] = sign
            if sign_type:
                data["sign_type"] = sign_type
            return result
        except Exception:
            logger.exception("Alipay verify_notify failed")
            return False

    async def query_payment(self, trade_no: str) -> dict:
        try:
            client = self._get_client()
            result = client.api_alipay_trade_query(trade_no=trade_no)
            status_map = {
                "TRADE_SUCCESS": "paid",
                "TRADE_FINISHED": "paid",
                "TRADE_CLOSED": "failed",
                "WAIT_BUYER_PAY": "pending",
            }
            return {
                "status": status_map.get(result.get("trade_status", ""), "unknown"),
                "trade_no": result.get("trade_no", trade_no),
                "raw": result,
            }
        except Exception:
            logger.exception("Alipay query_payment failed for %s", trade_no)
            return {"status": "unknown", "trade_no": trade_no}

    async def refund(self, trade_no: str, amount: Decimal, reason: str) -> dict:
        try:
            client = self._get_client()
            result = client.api_alipay_trade_refund(
                trade_no=trade_no,
                refund_amount=str(amount),
                refund_reason=reason,
            )
            success = result.get("fund_change") == "Y"
            logger.info(
                "Alipay refund %s for trade %s: %s",
                "succeeded" if success else "failed",
                trade_no,
                result,
            )
            return {"success": success, "raw": result}
        except Exception:
            logger.exception("Alipay refund failed for %s", trade_no)
            return {"success": False}


class WechatPayProvider(BasePaymentProvider):
    """WeChat Pay provider (API v3).

    Requires: pip install wechatpayv3
    Configure via environment variables:
      WECHAT_APP_ID, WECHAT_MCH_ID, WECHAT_API_KEY,
      WECHAT_CERT_SERIAL_NO, WECHAT_PRIVATE_KEY, WECHAT_NOTIFY_URL
    """

    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.mch_id = settings.wechat_mch_id
        self.api_key = settings.wechat_api_key
        self.cert_serial_no = settings.wechat_cert_serial_no
        self.private_key = settings.wechat_private_key
        self.notify_url = settings.wechat_notify_url

    def _get_client(self):
        """Lazy-load the WeChat Pay SDK client."""
        from wechatpayv3 import WeChatPay, WeChatPayType

        return WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=self.mch_id,
            private_key=self.private_key,
            cert_serial_no=self.cert_serial_no,
            appid=self.app_id,
            apiv3_key=self.api_key,
            notify_url=self.notify_url,
        )

    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> dict:
        try:
            client = self._get_client()
            # WeChat Pay amount is in cents (fen)
            amount_fen = int(amount * 100)
            code, result = client.pay(
                description=subject,
                out_trade_no=order_no,
                amount={"total": amount_fen, "currency": "CNY"},
            )
            if code == 200 and result.get("code_url"):
                logger.info("WeChat payment created for order %s", order_no)
                return {"pay_url": result["code_url"], "trade_no": None}
            logger.error("WeChat create_payment failed: %s %s", code, result)
            raise AppException(code=500, message="Payment creation failed")
        except AppException:
            raise
        except Exception:
            logger.exception("WeChat create_payment error for order %s", order_no)
            raise AppException(code=500, message="Payment creation failed")

    async def verify_notify(self, data: dict) -> bool:
        try:
            client = self._get_client()
            headers = data.get("headers", {})
            body = data.get("body", "")
            result = client.callback(headers=headers, body=body)
            return result is not None
        except Exception:
            logger.exception("WeChat verify_notify failed")
            return False

    async def query_payment(self, trade_no: str) -> dict:
        try:
            client = self._get_client()
            code, result = client.query(transaction_id=trade_no)
            if code != 200:
                return {"status": "unknown", "trade_no": trade_no}
            status_map = {
                "SUCCESS": "paid",
                "REFUND": "refunded",
                "NOTPAY": "pending",
                "CLOSED": "failed",
                "PAYERROR": "failed",
            }
            return {
                "status": status_map.get(result.get("trade_state", ""), "unknown"),
                "trade_no": result.get("transaction_id", trade_no),
                "raw": result,
            }
        except Exception:
            logger.exception("WeChat query_payment failed for %s", trade_no)
            return {"status": "unknown", "trade_no": trade_no}

    async def refund(self, trade_no: str, amount: Decimal, reason: str) -> dict:
        try:
            client = self._get_client()
            amount_fen = int(amount * 100)
            refund_no = f"R{uuid.uuid4().hex[:16]}"
            code, result = client.refund(
                transaction_id=trade_no,
                out_refund_no=refund_no,
                amount={"refund": amount_fen, "total": amount_fen, "currency": "CNY"},
                reason=reason,
            )
            success = code == 200 and result.get("status") == "SUCCESS"
            logger.info(
                "WeChat refund %s for trade %s: %s",
                "succeeded" if success else "failed",
                trade_no,
                result,
            )
            return {"success": success, "refund_no": refund_no, "raw": result}
        except Exception:
            logger.exception("WeChat refund failed for %s", trade_no)
            return {"success": False}


class MockPaymentProvider(BasePaymentProvider):
    """Mock payment provider for development and testing.

    Simulates successful payments without any external calls.
    """

    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> dict:
        mock_url = f"https://mock-pay.example.com/pay?order={order_no}&amount={amount}"
        logger.info("[MockPay] Payment created: order=%s amount=%s", order_no, amount)
        return {"pay_url": mock_url, "trade_no": f"MOCK_{uuid.uuid4().hex[:16]}"}

    async def verify_notify(self, data: dict) -> bool:
        logger.info("[MockPay] Notify verified (always True)")
        return True

    async def query_payment(self, trade_no: str) -> dict:
        logger.info("[MockPay] Query payment: %s -> paid", trade_no)
        return {"status": "paid", "trade_no": trade_no}

    async def refund(self, trade_no: str, amount: Decimal, reason: str) -> dict:
        logger.info("[MockPay] Refund: trade=%s amount=%s reason=%s", trade_no, amount, reason)
        return {"success": True, "refund_no": f"MOCK_R_{uuid.uuid4().hex[:8]}"}


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------


def get_payment_provider() -> BasePaymentProvider:
    """Return the payment provider based on config.

    Raises ValueError for unknown provider names.
    """
    name = settings.payment_provider.lower()
    if name == "alipay":
        return AlipayProvider()
    elif name == "wechat":
        return WechatPayProvider()
    elif name == "mock":
        return MockPaymentProvider()
    else:
        raise ValueError(f"Unknown payment provider: {name}")


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------


async def create_order_payment(
    db: AsyncSession,
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    method: str = "alipay",
) -> Payment:
    """Create a payment for an order.

    Validates:
    - Order exists and belongs to user
    - Order status is pending
    - No existing successful payment for this order
    - Payment amount matches order total

    Returns the created Payment with pay_url in notify_data.
    """
    # Fetch order
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundError("Order not found")

    # Verify ownership
    if order.user_id != user_id:
        raise ForbiddenError("Cannot pay for another user's order")

    # Verify order status
    if order.status != "pending":
        raise AppException(code=400, message="Only pending orders can be paid")

    # Check for existing successful payment
    existing = await db.execute(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.status == "paid",
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise AppException(code=400, message="Order already has a successful payment")

    # Resolve provider
    provider_map = {"alipay": "alipay", "wechat": "wechat", "mock": "mock"}
    if method not in provider_map:
        raise AppException(code=400, message=f"Unsupported payment method: {method}")

    # Create payment record
    payment = Payment(
        order_id=order_id,
        method=method,
        amount=order.total_amount,
        status="pending",
    )
    db.add(payment)
    await db.flush()

    # Call provider
    provider = get_payment_provider()
    pay_result = await provider.create_payment(
        order_no=order.order_no,
        amount=order.total_amount,
        subject=f"Order {order.order_no}",
    )

    # Store pay_url and trade_no
    payment.notify_data = {"pay_url": pay_result.get("pay_url")}
    if pay_result.get("trade_no"):
        payment.trade_no = pay_result["trade_no"]

    await db.flush()
    return payment


async def handle_payment_notify(
    db: AsyncSession,
    provider_name: str,
    notify_data: dict,
) -> bool:
    """Handle async payment callback from provider.

    Verifies signature, updates Payment and Order status.
    Idempotent: duplicate callbacks don't cause duplicate updates.

    Returns True if processed successfully.
    """
    # Determine provider
    if provider_name == "alipay":
        provider = AlipayProvider()
        order_no = notify_data.get("out_trade_no", "")
        trade_no = notify_data.get("trade_no", "")
        trade_status = notify_data.get("trade_status", "")
    elif provider_name == "wechat":
        provider = WechatPayProvider()
        # WeChat sends encrypted data; after decryption:
        resource = notify_data.get("resource", {})
        order_no = resource.get("out_trade_no", "")
        trade_no = resource.get("transaction_id", "")
        trade_status = resource.get("trade_state", "")
    else:
        logger.warning("Unknown payment provider in notify: %s", provider_name)
        return False

    # Verify signature
    if not await provider.verify_notify(notify_data):
        logger.warning("Payment notify signature verification failed for %s", order_no)
        return False

    # Find order
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()
    if order is None:
        logger.error("Payment notify: order not found: %s", order_no)
        return False

    # Find payment
    pay_result = await db.execute(
        select(Payment).where(
            Payment.order_id == order.id,
            Payment.status == "pending",
        )
    )
    payment = pay_result.scalar_one_or_none()
    if payment is None:
        # Already processed (idempotent) or no pending payment
        logger.info("Payment notify: no pending payment for order %s (idempotent)", order_no)
        return True

    # Check trade status
    success_statuses = {"TRADE_SUCCESS", "TRADE_FINISHED", "SUCCESS"}
    if trade_status not in success_statuses:
        logger.info("Payment notify: non-success status %s for order %s", trade_status, order_no)
        return True

    now = datetime.now(timezone.utc)

    # Update payment
    payment.status = "paid"
    payment.trade_no = trade_no
    payment.paid_at = now
    payment.notify_data = notify_data

    # Update order — handle cancelled order edge case
    if order.status == "cancelled":
        logger.warning(
            "Payment received for cancelled order %s, triggering refund", order_no
        )
        payment.notify_data = {**(payment.notify_data or {}), "_refund_needed": True}
        # Trigger async refund
        try:
            refund_result = await provider.refund(
                trade_no=trade_no,
                amount=payment.amount,
                reason="Order was cancelled before payment completed",
            )
            if refund_result.get("success"):
                payment.status = "refunded"
                logger.info("Auto-refund succeeded for order %s", order_no)
            else:
                logger.error("Auto-refund failed for order %s", order_no)
        except Exception:
            logger.exception("Auto-refund error for order %s", order_no)
    elif order.status == "pending":
        order.status = "paid"

    await db.flush()
    return True


async def query_payment_status(
    db: AsyncSession,
    payment_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict:
    """Query payment status.

    If already paid, returns DB status directly.
    If pending, queries the provider for latest status.
    Only allows querying own orders.
    """
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if payment is None:
        raise NotFoundError("Payment not found")

    # Verify ownership via order
    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalar_one_or_none()
    if order is None or order.user_id != user_id:
        raise ForbiddenError("Cannot query another user's payment")

    # If already paid, return directly
    if payment.status == "paid":
        return {
            "payment_id": str(payment.id),
            "order_id": str(payment.order_id),
            "method": payment.method,
            "amount": str(payment.amount),
            "status": payment.status,
            "trade_no": payment.trade_no,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        }

    # If pending and has trade_no, query provider
    if payment.status == "pending" and payment.trade_no:
        provider = get_payment_provider()
        remote = await provider.query_payment(payment.trade_no)
        if remote.get("status") == "paid":
            payment.status = "paid"
            payment.paid_at = datetime.now(timezone.utc)
            if order.status == "pending":
                order.status = "paid"
            await db.flush()

    return {
        "payment_id": str(payment.id),
        "order_id": str(payment.order_id),
        "method": payment.method,
        "amount": str(payment.amount),
        "status": payment.status,
        "trade_no": payment.trade_no,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
    }
