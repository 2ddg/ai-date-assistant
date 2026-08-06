"""数据库初始化：自动建库建表"""
import logging
import pymysql

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def _ensure_database():
    """连接前自动创建数据库（若不存在）"""
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset="utf8mb4",
        )
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        raise


engine = None
SessionLocal = None


def init_db():
    global engine, SessionLocal
    _ensure_database()
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    from models import user, persona, date_spot, chat
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成")
    return SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
