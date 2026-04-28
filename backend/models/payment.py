"""Model de Pago"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from datetime import datetime
import enum

from ..database import Base


class PaymentStatus(str, enum.Enum):
    """Estados de pago"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Métodos de pago"""
    STRIPE = "stripe"
    CASH = "cash"
    CHECK = "check"


class Payment(Base):
    """Modelo de Pago / Factura"""

    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    subscription_id = Column(
        String(36), ForeignKey("subscriptions.id"), nullable=True
    )

    amount_cents = Column(Integer, nullable=False)  # En centavos
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod), nullable=False)

    invoice_number = Column(String(50), unique=True, nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)

    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Payment {self.invoice_number} {self.status}>"
