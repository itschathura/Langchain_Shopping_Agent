from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes import chat, orders, preferences, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    # Attempt to initialize schema if database is reachable
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # Graceful start even if DB is temporarily offline
        pass
    yield


app = FastAPI(
    title="Multimodal Shopping Agent API",
    description="Production-ready, 100% Free-Tier Multimodal E-Commerce Shopping Assistant powered by LangChain & LangGraph.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(preferences.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Multimodal Shopping Agent API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
    }

