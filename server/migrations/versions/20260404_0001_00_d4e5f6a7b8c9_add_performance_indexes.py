"""add_performance_indexes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-04 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_consultations_status", "consultations", ["status"])
    op.create_index("ix_consultations_created_at", "consultations", ["created_at"])
    op.create_index("ix_ai_diagnosis_logs_created_at", "ai_diagnosis_logs", ["created_at"])
    op.create_index("ix_ai_diagnosis_logs_user_id", "ai_diagnosis_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_diagnosis_logs_user_id", table_name="ai_diagnosis_logs")
    op.drop_index("ix_ai_diagnosis_logs_created_at", table_name="ai_diagnosis_logs")
    op.drop_index("ix_consultations_created_at", table_name="consultations")
    op.drop_index("ix_consultations_status", table_name="consultations")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
