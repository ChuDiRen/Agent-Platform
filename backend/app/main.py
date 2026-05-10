from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def health():
    return {"status": "ok"}
