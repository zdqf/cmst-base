"""Property-based tests for Pydantic model roundtrip consistency.

**Validates: Requirements 17.4**

Property 2 (Roundtrip Consistency): For all valid Pydantic model instances,
serializing to JSON and deserializing back produces an equivalent instance.

    model == Model.model_validate_json(model.model_dump_json())
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import hypothesis.strategies as st
from hypothesis import given, settings

from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.ai import DiagnosisRequest, DiagnosisResponse, PairingRequest, PairingResponse
from app.schemas.consultation import ConsultationCreateRequest, ConsultationResponse
from app.schemas.cart import CartAddRequest, CartUpdateRequest, CartItemResponse
from app.schemas.order import CreateOrderRequest, OrderItemRequest, OrderItemResponse, OrderResponse
from app.schemas.common import ApiResponse, PaginationParams

# ---------------------------------------------------------------------------
# Reusable strategies
# ---------------------------------------------------------------------------

# Chinese mobile phone numbers: 1 + [3-9] + 9 digits
phone_st = st.from_regex(r"1[3-9]\d{9}", fullmatch=True)

uuid_st = st.uuids()

# Reasonable datetimes (timezone-aware UTC)
datetime_st = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2099, 12, 31),
    timezones=st.just(timezone.utc),
)

# Non-empty text for required string fields
nonempty_text_st = st.text(min_size=1, max_size=100).filter(lambda s: s.strip())

# Positive decimals with 2 decimal places for prices
price_st = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("99999.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

positive_int_st = st.integers(min_value=1, max_value=10000)


# ---------------------------------------------------------------------------
# Strategy builders for each model
# ---------------------------------------------------------------------------

@st.composite
def register_request_st(draw: st.DrawFn) -> RegisterRequest:
    return RegisterRequest(
        phone=draw(phone_st),
        code=draw(st.text(min_size=1, max_size=10)),
    )


@st.composite
def login_request_st(draw: st.DrawFn) -> LoginRequest:
    return LoginRequest(
        phone=draw(phone_st),
        code=draw(st.text(min_size=1, max_size=10)),
    )


@st.composite
def diagnosis_request_st(draw: st.DrawFn) -> DiagnosisRequest:
    return DiagnosisRequest(
        age=draw(st.integers(min_value=0, max_value=200)),
        gender=draw(st.sampled_from(["男", "女", "其他"])),
        symptoms=draw(nonempty_text_st),
        allergy_history=draw(st.text(max_size=200)),
        current_medication=draw(st.text(max_size=200)),
    )


@st.composite
def diagnosis_response_st(draw: st.DrawFn) -> DiagnosisResponse:
    return DiagnosisResponse(
        id=draw(uuid_st),
        result=draw(nonempty_text_st),
        created_at=draw(datetime_st),
    )


@st.composite
def pairing_request_st(draw: st.DrawFn) -> PairingRequest:
    ids = draw(st.lists(uuid_st, min_size=1, max_size=5))
    return PairingRequest(herb_ids=ids)


@st.composite
def pairing_response_st(draw: st.DrawFn) -> PairingResponse:
    return PairingResponse(result=draw(nonempty_text_st))


@st.composite
def consultation_request_st(draw: st.DrawFn) -> ConsultationCreateRequest:
    return ConsultationCreateRequest(
        name=draw(nonempty_text_st),
        contact=draw(nonempty_text_st),
        subject=draw(nonempty_text_st),
        description=draw(nonempty_text_st),
    )


@st.composite
def consultation_response_st(draw: st.DrawFn) -> ConsultationResponse:
    return ConsultationResponse(
        id=draw(uuid_st),
        name=draw(nonempty_text_st),
        contact=draw(nonempty_text_st),
        subject=draw(nonempty_text_st),
        description=draw(nonempty_text_st),
        status=draw(st.sampled_from(["pending", "processing", "completed"])),
        created_at=draw(datetime_st),
    )


@st.composite
def cart_add_request_st(draw: st.DrawFn) -> CartAddRequest:
    return CartAddRequest(
        product_id=draw(uuid_st),
        quantity=draw(positive_int_st),
    )


@st.composite
def cart_update_request_st(draw: st.DrawFn) -> CartUpdateRequest:
    return CartUpdateRequest(quantity=draw(positive_int_st))


@st.composite
def cart_item_response_st(draw: st.DrawFn) -> CartItemResponse:
    return CartItemResponse(
        id=draw(uuid_st),
        product_id=draw(uuid_st),
        product_name=draw(nonempty_text_st),
        quantity=draw(positive_int_st),
        unit_price=draw(price_st),
    )


@st.composite
def order_item_request_st(draw: st.DrawFn) -> OrderItemRequest:
    return OrderItemRequest(
        product_id=draw(uuid_st),
        quantity=draw(positive_int_st),
    )


@st.composite
def create_order_request_st(draw: st.DrawFn) -> CreateOrderRequest:
    items = draw(st.lists(order_item_request_st(), min_size=1, max_size=5))
    return CreateOrderRequest(items=items)


@st.composite
def order_item_response_st(draw: st.DrawFn) -> OrderItemResponse:
    return OrderItemResponse(
        product_id=draw(uuid_st),
        product_name=draw(nonempty_text_st),
        quantity=draw(positive_int_st),
        unit_price=draw(price_st),
    )


@st.composite
def order_response_st(draw: st.DrawFn) -> OrderResponse:
    items = draw(st.lists(order_item_response_st(), min_size=1, max_size=5))
    return OrderResponse(
        id=draw(uuid_st),
        order_no=draw(nonempty_text_st),
        total_amount=draw(price_st),
        status=draw(st.sampled_from(["pending", "paid", "shipped", "completed", "cancelled"])),
        items=items,
        created_at=draw(datetime_st),
    )


@st.composite
def api_response_st(draw: st.DrawFn) -> ApiResponse:
    return ApiResponse(
        code=draw(st.integers(min_value=0, max_value=9999)),
        message=draw(st.text(max_size=200)),
        data=draw(st.none() | st.text(max_size=100) | st.integers()),
    )


@st.composite
def pagination_params_st(draw: st.DrawFn) -> PaginationParams:
    return PaginationParams(
        page=draw(st.integers(min_value=1, max_value=1000)),
        page_size=draw(st.integers(min_value=1, max_value=20)),
    )


# ---------------------------------------------------------------------------
# Roundtrip property tests
# ---------------------------------------------------------------------------

def _assert_roundtrip(model_instance, model_class):
    """Assert JSON roundtrip produces an equivalent instance."""
    json_str = model_instance.model_dump_json()
    restored = model_class.model_validate_json(json_str)
    assert model_instance == restored, (
        f"Roundtrip failed:\n  original={model_instance}\n  restored={restored}"
    )


class TestAuthRoundtrip:
    """Roundtrip tests for authentication schemas."""

    @given(instance=register_request_st())
    @settings(max_examples=100)
    def test_register_request(self, instance: RegisterRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, RegisterRequest)

    @given(instance=login_request_st())
    @settings(max_examples=100)
    def test_login_request(self, instance: LoginRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, LoginRequest)


class TestAIRoundtrip:
    """Roundtrip tests for AI diagnosis schemas."""

    @given(instance=diagnosis_request_st())
    @settings(max_examples=100)
    def test_diagnosis_request(self, instance: DiagnosisRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, DiagnosisRequest)

    @given(instance=diagnosis_response_st())
    @settings(max_examples=100)
    def test_diagnosis_response(self, instance: DiagnosisResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, DiagnosisResponse)

    @given(instance=pairing_request_st())
    @settings(max_examples=100)
    def test_pairing_request(self, instance: PairingRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, PairingRequest)

    @given(instance=pairing_response_st())
    @settings(max_examples=100)
    def test_pairing_response(self, instance: PairingResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, PairingResponse)


class TestConsultationRoundtrip:
    """Roundtrip tests for consultation schemas."""

    @given(instance=consultation_request_st())
    @settings(max_examples=100)
    def test_consultation_request(self, instance: ConsultationCreateRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, ConsultationCreateRequest)

    @given(instance=consultation_response_st())
    @settings(max_examples=100)
    def test_consultation_response(self, instance: ConsultationResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, ConsultationResponse)


class TestCartRoundtrip:
    """Roundtrip tests for cart schemas."""

    @given(instance=cart_add_request_st())
    @settings(max_examples=100)
    def test_cart_add_request(self, instance: CartAddRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, CartAddRequest)

    @given(instance=cart_update_request_st())
    @settings(max_examples=100)
    def test_cart_update_request(self, instance: CartUpdateRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, CartUpdateRequest)

    @given(instance=cart_item_response_st())
    @settings(max_examples=100)
    def test_cart_item_response(self, instance: CartItemResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, CartItemResponse)


class TestOrderRoundtrip:
    """Roundtrip tests for order schemas."""

    @given(instance=create_order_request_st())
    @settings(max_examples=100)
    def test_create_order_request(self, instance: CreateOrderRequest) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, CreateOrderRequest)

    @given(instance=order_item_response_st())
    @settings(max_examples=100)
    def test_order_item_response(self, instance: OrderItemResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, OrderItemResponse)

    @given(instance=order_response_st())
    @settings(max_examples=100)
    def test_order_response(self, instance: OrderResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, OrderResponse)


class TestCommonRoundtrip:
    """Roundtrip tests for common schemas."""

    @given(instance=api_response_st())
    @settings(max_examples=100)
    def test_api_response(self, instance: ApiResponse) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, ApiResponse)

    @given(instance=pagination_params_st())
    @settings(max_examples=100)
    def test_pagination_params(self, instance: PaginationParams) -> None:
        """**Validates: Requirements 17.4**"""
        _assert_roundtrip(instance, PaginationParams)
