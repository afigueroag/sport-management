"""
SportAcademia API - FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db, close_db

# Importar routers
from routers import auth, students, classes, enrollments, attendance, class_sessions, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events para la aplicación"""
    # Startup
    print("🚀 SportAcademia API starting...")
    await init_db()
    print("✓ Database initialized")
    yield
    # Shutdown
    print("🛑 SportAcademia API shutting down...")
    await close_db()
    print("✓ Database closed")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para gestión de academias de deportes",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])

# Incluir router de clases
app.include_router(classes.router, prefix="/api/classes", tags=["Classes"])

# Incluir router de inscripciones
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["Enrollments"])

# Incluir router de asistencia
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])

# Incluir router de sesiones de clase
app.include_router(class_sessions.router, prefix="/api/class-sessions", tags=["Class Sessions"])

# Incluir router de dashboard
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# Próximos routers (Phase 5+)
# app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
