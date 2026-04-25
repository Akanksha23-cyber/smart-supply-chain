"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.database import Base, engine
from app.utils.logging_config import configure_logging
from app.utils.graph_db import graph_db
from app.routers import shipments, events, predictions, routes, admin, websocket

# Configure logging
configure_logging()

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Supply Chain Backend Starting...")
    print(f"📊 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
    print(f"⚡ Redis: {settings.redis_url}")
    print(f"🔗 Neo4j: {settings.neo4j_uri}")

    yield

    # Shutdown
    print("🛑 Shutting down Supply Chain Backend...")
    graph_db.close()


# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Resilient Logistics & Supply Chain Optimization System",
    description="Production-grade backend for dynamic supply chain management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(shipments.router)
app.include_router(events.router)
app.include_router(predictions.router)
app.include_router(routes.router)
app.include_router(admin.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Real-Time Resilient Logistics & Supply Chain Optimization System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health():
    """Quick health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
