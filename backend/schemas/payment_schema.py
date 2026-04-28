"""Payment and Subscription schemas for Stripe integration"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.payment import PaymentStatus, PaymentMethod
from ..models.subscription import SubscriptionStatus


class CheckoutSessionRequest(BaseModel):
    """Schema para crear una sesión de checkout de Stripe"""
    membership_id: str


class CheckoutSessionResponse(BaseModel):
    """Respuesta con URL de checkout"""
    checkout_url: str
    session_id: str


class PaymentResponse(BaseModel):
    """Schema para responder con datos de pago"""
    id: str
    student_id: str
    subscription_id: Optional[str]
    amount_cents: int
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    invoice_number: Optional[str]
    stripe_payment_intent_id: Optional[str]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Schema para responder con datos de suscripción"""
    id: str
    student_id: str
    membership_id: str
    status: SubscriptionStatus
    stripe_subscription_id: Optional[str]
    started_at: datetime
    current_period_end: Optional[datetime]
    canceled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerPortalRequest(BaseModel):
    """Schema para solicitar URL del portal de cliente"""
    return_url: str = Field(default="http://localhost:3000/dashboard")
