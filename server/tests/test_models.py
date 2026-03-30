"""Tests for ORM model structure — field definitions, constraints, and relationships (Task 1.4).

These are pure model-structure tests that inspect SQLAlchemy metadata.
No database connection is needed.

Validates: Requirements 16.2, 16.5
"""

import uuid

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.types import String, Text, Integer, Numeric, Boolean, DateTime

from app.models import (
    AIDiagnosisLog,
    CartItem,
    ComplianceWord,
    Consultation,
    Herb,
    Order,
    OrderItem,
    Product,
    PromptTemplate,
    StockLog,
    User,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_MODELS = [
    User, Herb, AIDiagnosisLog, Consultation, Product,
    Order, OrderItem, CartItem, PromptTemplate, ComplianceWord, StockLog,
]

MODELS_WITH_UPDATED_AT = [
    m for m in ALL_MODELS if m is not StockLog
]


def _cols(model):
    """Return the __table__.columns collection for a model."""
    return model.__table__.columns


def _col(model, name):
    """Return a single Column object by name."""
    return _cols(model)[name]


# ---------------------------------------------------------------------------
# 1. __tablename__
# ---------------------------------------------------------------------------

class TestTableNames:
    def test_user_tablename(self):
        assert User.__tablename__ == "users"

    def test_herb_tablename(self):
        assert Herb.__tablename__ == "herbs"

    def test_ai_diagnosis_log_tablename(self):
        assert AIDiagnosisLog.__tablename__ == "ai_diagnosis_logs"

    def test_consultation_tablename(self):
        assert Consultation.__tablename__ == "consultations"

    def test_product_tablename(self):
        assert Product.__tablename__ == "products"

    def test_order_tablename(self):
        assert Order.__tablename__ == "orders"

    def test_order_item_tablename(self):
        assert OrderItem.__tablename__ == "order_items"

    def test_cart_item_tablename(self):
        assert CartItem.__tablename__ == "cart_items"

    def test_prompt_template_tablename(self):
        assert PromptTemplate.__tablename__ == "prompt_templates"

    def test_compliance_word_tablename(self):
        assert ComplianceWord.__tablename__ == "compliance_words"

    def test_stock_log_tablename(self):
        assert StockLog.__tablename__ == "stock_logs"


# ---------------------------------------------------------------------------
# 2. UUID primary keys
# ---------------------------------------------------------------------------

class TestUUIDPrimaryKeys:
    def test_all_models_have_uuid_pk(self):
        for model in ALL_MODELS:
            col = _col(model, "id")
            assert col.primary_key, f"{model.__name__}.id should be primary key"
            assert isinstance(col.type, UUID), (
                f"{model.__name__}.id should be UUID, got {type(col.type)}"
            )


# ---------------------------------------------------------------------------
# 3. Timestamp fields (created_at / updated_at)
# ---------------------------------------------------------------------------

class TestTimestampFields:
    def test_all_models_have_created_at(self):
        for model in ALL_MODELS:
            col = _col(model, "created_at")
            assert isinstance(col.type, DateTime), (
                f"{model.__name__}.created_at should be DateTime"
            )

    def test_models_with_updated_at(self):
        for model in MODELS_WITH_UPDATED_AT:
            col = _col(model, "updated_at")
            assert isinstance(col.type, DateTime), (
                f"{model.__name__}.updated_at should be DateTime"
            )

    def test_stock_log_has_no_updated_at(self):
        col_names = [c.name for c in _cols(StockLog)]
        assert "updated_at" not in col_names


# ---------------------------------------------------------------------------
# 4. Unique constraints (single-column)
# ---------------------------------------------------------------------------

class TestUniqueConstraints:
    def test_user_phone_unique(self):
        assert _col(User, "phone").unique is True

    def test_herb_name_unique(self):
        assert _col(Herb, "name").unique is True

    def test_order_order_no_unique(self):
        assert _col(Order, "order_no").unique is True

    def test_compliance_word_forbidden_word_unique(self):
        assert _col(ComplianceWord, "forbidden_word").unique is True


# ---------------------------------------------------------------------------
# 5. Composite unique constraints
# ---------------------------------------------------------------------------

class TestCompositeUniqueConstraints:
    def _get_unique_constraint_columns(self, model):
        """Return a list of frozensets, each containing column names of a unique constraint."""
        from sqlalchemy import UniqueConstraint
        result = []
        for constraint in model.__table__.constraints:
            if isinstance(constraint, UniqueConstraint):
                result.append(frozenset(c.name for c in constraint.columns))
        return result

    def test_cart_item_user_product_unique(self):
        uqs = self._get_unique_constraint_columns(CartItem)
        assert frozenset({"user_id", "product_id"}) in uqs

    def test_prompt_template_type_version_unique(self):
        uqs = self._get_unique_constraint_columns(PromptTemplate)
        assert frozenset({"type", "version"}) in uqs


# ---------------------------------------------------------------------------
# 6. Foreign key relationships
# ---------------------------------------------------------------------------

class TestForeignKeys:
    def _fk_targets(self, model):
        """Return a set of 'table.column' strings for all FKs on the model."""
        targets = set()
        for col in _cols(model):
            for fk in col.foreign_keys:
                targets.add(fk.target_fullname)
        return targets

    def test_ai_diagnosis_log_fk_user(self):
        assert "users.id" in self._fk_targets(AIDiagnosisLog)

    def test_consultation_fk_user(self):
        targets = self._fk_targets(Consultation)
        assert "users.id" in targets  # user_id and handled_by both reference users.id

    def test_order_fk_user(self):
        assert "users.id" in self._fk_targets(Order)

    def test_order_item_fk_order(self):
        targets = self._fk_targets(OrderItem)
        assert "orders.id" in targets

    def test_order_item_fk_product(self):
        targets = self._fk_targets(OrderItem)
        assert "products.id" in targets

    def test_cart_item_fk_user(self):
        assert "users.id" in self._fk_targets(CartItem)

    def test_cart_item_fk_product(self):
        assert "products.id" in self._fk_targets(CartItem)

    def test_stock_log_fk_product(self):
        assert "products.id" in self._fk_targets(StockLog)

    def test_stock_log_fk_operator(self):
        assert "users.id" in self._fk_targets(StockLog)


# ---------------------------------------------------------------------------
# 7. Field types
# ---------------------------------------------------------------------------

class TestFieldTypes:
    # JSON
    def test_ai_diagnosis_log_input_data_is_json(self):
        assert isinstance(_col(AIDiagnosisLog, "input_data").type, JSON)

    # Numeric (prices)
    def test_product_price_is_numeric(self):
        col_type = _col(Product, "price").type
        assert isinstance(col_type, Numeric)

    def test_order_total_amount_is_numeric(self):
        col_type = _col(Order, "total_amount").type
        assert isinstance(col_type, Numeric)

    def test_order_item_unit_price_is_numeric(self):
        col_type = _col(OrderItem, "unit_price").type
        assert isinstance(col_type, Numeric)

    # Integer
    def test_product_stock_is_integer(self):
        assert isinstance(_col(Product, "stock").type, Integer)

    def test_order_item_quantity_is_integer(self):
        assert isinstance(_col(OrderItem, "quantity").type, Integer)

    def test_cart_item_quantity_is_integer(self):
        assert isinstance(_col(CartItem, "quantity").type, Integer)

    def test_stock_log_change_amount_is_integer(self):
        assert isinstance(_col(StockLog, "change_amount").type, Integer)

    def test_prompt_template_version_is_integer(self):
        assert isinstance(_col(PromptTemplate, "version").type, Integer)

    # Boolean
    def test_prompt_template_is_active_is_boolean(self):
        assert isinstance(_col(PromptTemplate, "is_active").type, Boolean)

    # Text
    def test_ai_diagnosis_log_ai_output_is_text(self):
        assert isinstance(_col(AIDiagnosisLog, "ai_output").type, Text)

    def test_consultation_description_is_text(self):
        assert isinstance(_col(Consultation, "description").type, Text)

    def test_prompt_template_content_is_text(self):
        assert isinstance(_col(PromptTemplate, "content").type, Text)

    # String
    def test_user_phone_is_string(self):
        assert isinstance(_col(User, "phone").type, String)

    def test_herb_name_is_string(self):
        assert isinstance(_col(Herb, "name").type, String)

    def test_order_order_no_is_string(self):
        assert isinstance(_col(Order, "order_no").type, String)
