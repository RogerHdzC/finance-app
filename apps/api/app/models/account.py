import uuid
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal
from app.db.base import Base
from app.models.mixin.timestamp import TimestampMixin
from sqlalchemy import String, Numeric, Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

class AccountType(str, Enum):
    debit = "debit"
    credit = "credit"
    cash = "cash"

class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    bank: Mapped[str] = mapped_column(String(50), nullable=True)
    type: Mapped[AccountType] = mapped_column(SAEnum(AccountType,name="account_type", create_type=True), nullable=False)  # debit, credit, cash
    currency: Mapped[str] = mapped_column(String(3), nullable=False) # MXN, USD, EUR, etc.
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=True)