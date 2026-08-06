import os
from dotenv import load_dotenv

load_dotenv()

# ============ LLM 配置（智谱 GLM-4 系列） ============
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
LLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 成本感知路由
COST_AWARE_MODELS = {
    "cheap": "glm-4-flash",     # 简单任务：情绪识别、工具结果摘要
    "medium": "glm-4-air",      # 中等任务：人格回复、地点描述
    "premium": "glm-4",         # 复杂任务：Agent 推理、约会方案规划
}

# 视觉模型（穿搭评价）
VISION_MODEL = "glm-4v-flash"

# ============ 百度地图 Agent Plan ============
# 持久化在 .env / 用户环境变量中
BAIDU_MAP_AUTH_TOKEN = os.getenv("BAIDU_MAP_AUTH_TOKEN", "")

# ============ Agent 配置 ============
AGENT_MAX_ITERATIONS = 5          # 单轮对话最大工具调用次数
AGENT_MAX_RETRY = 2               # 工具失败重试次数
WEATHER_API_URL = "https://wttr.in/{city}?format=3"   # 免费天气 API

# ============ MySQL 数据库配置 ============
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ai_date_assistant")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
)

# ============ JWT 认证配置 ============
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai-date-assistant-secret-key-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# ============ 其他 ============
UPLOAD_DIR = "./uploads"
