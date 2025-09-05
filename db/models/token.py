
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Text
import datetime
import pytz
from db.models.base import Base


class AppToken(Base):
    __tablename__ = "app_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False)
    userid = Column(BigInteger, nullable=False)
    appid = Column(BigInteger, nullable=False)
    access_token = Column(Text, nullable=False)
    expires_in = Column(Integer, nullable=False)
    refresh_token = Column(Text, nullable=False)
    refresh_token_expires_in = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), nullable=False)


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增ID")
    caller = Column(String(128), nullable=False, comment="调用人")
    caller_ip = Column(String(64), nullable=False, comment="调用者IP")
    called_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), nullable=False, comment="调用时间")