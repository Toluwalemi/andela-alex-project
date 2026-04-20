from fastapi import APIRouter

from app.api.routes import analysis, health, me, portfolios, retirement

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(me.router, prefix="/api/v1", tags=["me"])
api_router.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["portfolios"])
api_router.include_router(retirement.router, prefix="/api/v1", tags=["retirement"])
api_router.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

