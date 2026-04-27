"""User Service - Business logic for user operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import uuid

from models.user import User, UserRole
from models.student import Student
from schemas.user import UserCreate
from utils.security import hash_password


async def create_user(db: AsyncSession, user_data: UserCreate, role: UserRole = UserRole.STUDENT):
    """Crea un nuevo usuario"""
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email.lower(),
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=role,
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        return None  # Email already exists


async def create_student(db: AsyncSession, user_data: UserCreate):
    """Crea un nuevo usuario con rol STUDENT"""
    user = await create_user(db, user_data, UserRole.STUDENT)

    if user:
        # Crear registro de Student
        student = Student(id=user.id)
        db.add(student)
        await db.commit()
        await db.refresh(student)

    return user


async def get_user_by_email(db: AsyncSession, email: str):
    """Obtiene un usuario por email"""
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str):
    """Obtiene un usuario por ID"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalars().first()


async def user_exists(db: AsyncSession, email: str) -> bool:
    """Verifica si un usuario existe por email"""
    user = await get_user_by_email(db, email)
    return user is not None


async def get_active_user(db: AsyncSession, user_id: str):
    """Obtiene un usuario activo por ID"""
    user = await get_user_by_id(db, user_id)
    if user and user.is_active:
        return user
    return None
