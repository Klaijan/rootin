# app/main.py - Clean FastAPI initialization
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api_router
from app.core.db import data_manager

def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title="Skincare Wellbeing App",
        description="AI-enhanced skincare routine analysis and recommendations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix="/api", tags=["api"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "data_loaded": not data_manager.ingredients.empty,
            "total_ingredients": len(data_manager.ingredients),
            "total_products": len(data_manager.products),
            "total_interactions": len(data_manager.interactions)
        }

    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
