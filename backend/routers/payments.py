"""
Payments Router - Stripe payment integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import stripe
import uuid

from ..config import settings
from ..database import get_db
from ..models.student import Student
from ..models.user import User
from ..models.membership import Membership
from ..models.subscription import Subscription, SubscriptionStatus
from ..models.payment import Payment, PaymentStatus, PaymentMethod
from ..schemas.payment_schema import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PaymentResponse,
    SubscriptionResponse,
    CustomerPortalRequest,
)
from .auth import get_current_user

# Configurar API key de Stripe
stripe.api_key = settings.stripe_secret_key

router = APIRouter(tags=["Payments"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una sesión de checkout de Stripe para una suscripción

    El estudiante puede crear sesiones solo para sí mismo
    """
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden crear sesiones de pago",
        )

    # Verificar que la membresía existe
    result = await db.execute(
        select(Membership).where(Membership.id == request.membership_id)
    )
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membresía no encontrada",
        )

    # Crear sesión de checkout en Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=current_user.email,
            client_reference_id=current_user.id,
            line_items=[
                {
                    "price": membership.stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url="http://localhost:3000/dashboard?payment=success",
            cancel_url="http://localhost:3000/dashboard?payment=canceled",
        )

        return CheckoutSessionResponse(
            checkout_url=session.url,
            session_id=session.id,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de Stripe: {str(e)}",
        )


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista las suscripciones del estudiante actual
    """
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden ver suscripciones",
        )

    result = await db.execute(
        select(Subscription).where(Subscription.student_id == current_user.id)
    )
    subscriptions = result.scalars().all()

    return subscriptions


@router.get("/history", response_model=list[PaymentResponse])
async def get_payment_history(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista el historial de pagos del estudiante
    """
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden ver historial de pagos",
        )

    result = await db.execute(
        select(Payment)
        .where(Payment.student_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    payments = result.scalars().all()

    return payments


@router.post("/portal")
async def create_customer_portal(
    request: CustomerPortalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una URL del portal de cliente de Stripe

    Permite al estudiante gestionar su suscripción (cambiar plan, cancelar, etc.)
    """
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden acceder al portal",
        )

    # Obtener la suscripción del estudiante
    result = await db.execute(
        select(Subscription).where(
            Subscription.student_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
    )
    subscription = result.scalars().first()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes una suscripción activa",
        )

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_subscription_id.split("_")[0],  # Extract customer ID
            return_url=request.return_url,
        )

        return {
            "portal_url": portal_session.url,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de Stripe: {str(e)}",
        )


@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Maneja webhooks de Stripe para eventos de suscripción

    Actualiza el estado de las suscripciones y crea registros de pago
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # Manejar eventos de Stripe
    if event["type"] == "invoice.paid":
        await handle_invoice_paid(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_failed":
        await handle_invoice_payment_failed(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_deleted(event["data"]["object"], db)

    return {"status": "success"}


async def handle_invoice_paid(invoice: dict, db: AsyncSession):
    """Maneja pago exitoso de factura"""
    # Buscar la suscripción
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == invoice.get("subscription")
        )
    )
    subscription = result.scalars().first()

    if subscription:
        subscription.status = SubscriptionStatus.ACTIVE

        # Crear registro de pago
        payment = Payment(
            id=str(uuid.uuid4()),
            student_id=subscription.student_id,
            subscription_id=subscription.id,
            amount_cents=invoice.get("amount_paid"),
            currency=invoice.get("currency", "usd"),
            status=PaymentStatus.PAID,
            payment_method=PaymentMethod.STRIPE,
            invoice_number=invoice.get("number"),
            stripe_payment_intent_id=invoice.get("payment_intent"),
            paid_at=datetime.utcnow(),
        )
        db.add(payment)
        await db.commit()


async def handle_invoice_payment_failed(invoice: dict, db: AsyncSession):
    """Maneja fallo de pago de factura"""
    # Buscar la suscripción
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == invoice.get("subscription")
        )
    )
    subscription = result.scalars().first()

    if subscription:
        # Crear registro de pago fallido
        payment = Payment(
            id=str(uuid.uuid4()),
            student_id=subscription.student_id,
            subscription_id=subscription.id,
            amount_cents=invoice.get("amount_due"),
            currency=invoice.get("currency", "usd"),
            status=PaymentStatus.FAILED,
            payment_method=PaymentMethod.STRIPE,
            invoice_number=invoice.get("number"),
            stripe_payment_intent_id=invoice.get("payment_intent"),
            due_date=datetime.fromtimestamp(invoice.get("due_date", 0)),
        )
        db.add(payment)
        await db.commit()


async def handle_subscription_deleted(subscription_data: dict, db: AsyncSession):
    """Maneja cancelación de suscripción"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_data.get("id")
        )
    )
    subscription = result.scalars().first()

    if subscription:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
        await db.commit()
