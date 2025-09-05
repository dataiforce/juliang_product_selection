from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import Config


engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Session:
    """
    返回一个 SQLAlchemy Session 实例
    使用完毕需手动关闭或通过上下文管理自动关闭
    """
    return SessionLocal()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
