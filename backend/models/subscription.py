"""Model de Suscripción"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum
from datetime import datetime
import enum

from ..database import Base


class SubscriptionStatus(str, enum.Enum):
    """Estados de suscripción"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"
    PENDING = "pending"


class Subscription(Base):
    """Modelo de Suscripción (Student → Membership)"""

    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    membership_id = Column(
        String(36), ForeignKey("memberships.id"), nullable=False
    )
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    stripe_subscription_id = Column(String(255), nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_period_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Subscription student={self.student_id} status={self.status}>"
