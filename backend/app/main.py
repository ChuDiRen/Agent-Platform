import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User
from app.models.agent import Agent
from app.api.v1.endpoints import (
    users,
    projects,
    agents,
    test_data,
    documents,
    api_documents,
    test_cases,
    api_automation,
    ui_automation,
    performance,
)

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
app.include_router(projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["projects"])
app.include_router(agents.router, prefix=f"{settings.API_V1_PREFIX}/agents", tags=["agents"])
app.include_router(test_data.router, prefix=f"{settings.API_V1_PREFIX}/test-data", tags=["test-data"])
app.include_router(test_cases.router, prefix=f"{settings.API_V1_PREFIX}/test-cases", tags=["test-cases"])
app.include_router(documents.router, prefix=f"{settings.API_V1_PREFIX}/documents", tags=["documents"])
app.include_router(api_documents.router, prefix=f"{settings.API_V1_PREFIX}/api-documents", tags=["api-documents"])
app.include_router(api_automation.router, prefix=f"{settings.API_V1_PREFIX}/api-automation", tags=["api-automation"])
app.include_router(ui_automation.router, prefix=f"{settings.API_V1_PREFIX}/ui-automation", tags=["ui-automation"])
app.include_router(performance.router, prefix=f"{settings.API_V1_PREFIX}/performance", tags=["performance"])


SEED_AGENTS = [
    {
        "name": "AI需求评估助手",
        "description": "我是你的需求文档小管家，能快速帮你找出文档里没说清楚的地方和可能存在的问题，让需求更清晰～",
        "tags": '["需求分析","提交立项","文档管理","用线性","场景分析","一键AI测试"]',
        "icon": "doc",
        "gradient": "linear-gradient(135deg, #3b82f6, #6366f1)",
        "sort_order": 1,
    },
    {
        "name": "AI测试用例智能体",
        "description": "我超会的写测试用例，各种测试场景信手来，帮你把功能给得明白白！",
        "tags": '["场景分析","用线性","一键AI测试"]',
        "icon": "testcase",
        "gradient": "linear-gradient(135deg, #8b5cf6, #a855f7)",
        "sort_order": 2,
    },
    {
        "name": "AI界面UI自动化脚本",
        "description": "点点界面这种事就不劳烦大人您了，WEB和APP都交给我，你喝杯咖啡等着出结果就好～",
        "tags": "[]",
        "icon": "ui",
        "gradient": "linear-gradient(135deg, #ec4899, #f43f5e)",
        "sort_order": 3,
    },
    {
        "name": "AI接口文档分析",
        "description": "接口文档太复杂看不懂？我来帮你理得清清楚楚，还能跳出不合规的地方！",
        "tags": '["接口解析","文档分析","规范检查"]',
        "icon": "api-doc",
        "gradient": "linear-gradient(135deg, #14b8a6, #06b6d4)",
        "sort_order": 4,
    },
    {
        "name": "AI接口用例设计助手",
        "description": "接口怎么测更全面？我来帮你设计测试思路，各种参数组合都不放过！",
        "tags": '["接口用例","用例设计"]',
        "icon": "api-case",
        "gradient": "linear-gradient(135deg, #f59e0b, #f97316)",
        "sort_order": 5,
    },
    {
        "name": "AI接口自动化脚本助手",
        "description": "一键生成测试接口测试，自动断言、出报告，省心省力交给我～",
        "tags": '["一键AI测试","断言判断","测试报告"]',
        "icon": "api-auto",
        "gradient": "linear-gradient(135deg, #10b981, #22c55e)",
        "sort_order": 6,
    },
    {
        "name": "AI测试数据生成智能体",
        "description": "想要什么样的测试数据？跟我说，合理的数字、刁钻的数据，我都能变出来！",
        "tags": '["数据生成","规范检查"]',
        "icon": "data",
        "gradient": "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "sort_order": 7,
    },
    {
        "name": "AI性能数据分析助手",
        "description": "性能报告太枯燥？我来帮你分析哪里慢，为什么慢，还能给出提速小贴士！",
        "tags": '["断言解析","优化建议"]',
        "icon": "perf",
        "gradient": "linear-gradient(135deg, #ef4444, #f97316)",
        "sort_order": 8,
    },
    {
        "name": "更多智能体即将上线",
        "description": "我们正在不断训练新的数字员工，敬请期待～",
        "tags": "[]",
        "icon": "more",
        "gradient": "linear-gradient(135deg, #94a3b8, #cbd5e1)",
        "sort_order": 9,
        "is_placeholder": True,
    },
]


@app.on_event("startup")
def seed_defaults():
    """启动时自动创建默认管理员和智能体数据（如不存在）。"""
    db = SessionLocal()
    try:
        # Seed admin
        if not db.query(User).filter(User.email == "admin@qq.com").first():
            db.add(User(
                email="admin@qq.com",
                hashed_password=get_password_hash("admin123456"),
                full_name="管理员",
                is_active=True,
                is_superuser=True,
            ))
            db.commit()

        # Seed agents
        if db.query(Agent).count() == 0:
            for data in SEED_AGENTS:
                db.add(Agent(**data))
            db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def health():
    return {"status": "ok"}

