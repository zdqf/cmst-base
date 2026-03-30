"""Admin user management Pydantic schemas.

Requirements:
- 8.1: User list with phone, registration time, last login time
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminUserItem(BaseModel):
    """User item for admin user list."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    nickname: str | None = None
    status: str
    is_admin: bool = False
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
