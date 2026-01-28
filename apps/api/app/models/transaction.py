import uuid
from uuid import UUID
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Any

from app.db.base import Base
from app.models.mixin.timestamp import TimestampMixin
from sqlalchemy import String, Numeric, Enum as SAEnum, Index, UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionSource(str, Enum):
    manual = "manual"
    imported = "imported"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    transfer_group_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType,name="transaction_type", create_type=True), nullable=False)  # income, expense
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[TransactionSource] = mapped_column(SAEnum(TransactionSource, name="transaction_source", create_type=True), nullable=False)  # e.g., 'manual', 'imported', etc.
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ID from external systems if applicable
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)  # Store raw JSON or data from external sources
    hash_dedupe: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash for deduplication
    
    __table_args__ = (
        Index('ix_transactions_user_date', 'user_id', 'date'),
        Index('ix_transactions_account_date', 'account_id', 'date'),
        UniqueConstraint('user_id','hash_dedupe', name='uq_transactions_user_hash_dedupe'),
    )