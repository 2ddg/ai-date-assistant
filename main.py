import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import auth, chat, outfit, personas, spots
from core.persona import ensure_default_personas

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        session_factory = init_db()
        db = session_factory()
        try:
            ensure_default_personas(db)
        finally:
            db.close()
        print("=" * 50)
        print("  AI 约会助手启动成功！")
        print("  API 文档: http://localhost:8080/docs")
        if os.path.exists(FRONTEND_DIST):
            print("  前端页面: http://localhost:8080/")
        else:
            print("  前端未构建，请运行: cd frontend && npm run build")
        print("=" * 50)
    except Exception as e:
        logger.error(f"启动初始化失败: {e}")
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(title="AI约会助手", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(outfit.router)
app.include_router(spots.router)
app.include_router(personas.router)

os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# 挂载上传文件目录（必须在前端挂载之前，因为 / 会吃掉所有路径）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 挂载前端静态文件（如果已构建）
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "AI约会助手运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
