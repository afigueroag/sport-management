"""Model de Membresía (Plan)"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime

from database import Base


class Membership(Base):
    """Modelo de Plan de Membresía"""

    __tablename__ = "memberships"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # e.g., "Monthly Unlimited"
    description = Column(String(500), nullable=True)
    price_cents = Column(Integer, nullable=False)  # En centavos (ej: 7900 = $79.00)
    currency = Column(String(3), default="USD", nullable=False)
    class_limit = Column(Integer, nullable=True)  # null = unlimited
    duration_months = Column(Integer, default=1, nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Membership {self.name}>"
