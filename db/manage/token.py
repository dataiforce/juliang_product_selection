from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from db.models.token import AppToken, ApiCallLog


def update_token_by_appid(
    session: Session,
    appid: int,
    access_token: str,
    expires_in: int,
    refresh_token: str,
    refresh_token_expires_in: int,
) -> bool:
    """
    根据 appid 更新 token 信息
    :param session: SQLAlchemy Session
    :param appid: 应用ID
    :param access_token: 新 access_token
    :param expires_in: access_token 有效期（秒）
    :param refresh_token: 新 refresh_token
    :param refresh_token_expires_in: refresh_token 有效期（秒）
    :return: True 更新成功, False 未找到
    """
    token: AppToken | None = session.execute(
        select(AppToken).where(AppToken.appid == appid)
    ).scalar_one_or_none()

    if not token:
        return False

    token.access_token = access_token
    token.expires_in = expires_in
    token.refresh_token = refresh_token
    token.refresh_token_expires_in = refresh_token_expires_in
    token.updated_at = datetime.utcnow()

    session.commit()
    return True


def get_refresh_token_by_appid(session: Session, appid: int) -> str | None:
    """
    根据 appid 查询 refresh_token
    :param session: SQLAlchemy Session
    :param appid: 应用ID
    :return: refresh_token (字符串) 或 None
    """
    result = session.execute(
        select(AppToken.refresh_token).where(AppToken.appid == appid)
    ).scalar_one_or_none()
    return result


def get_app_token_by_appid(session: Session, appid: int) -> dict | None:
    """
    根据 appid 查询 AppToken 记录，并计算剩余有效期
    :param session: SQLAlchemy Session
    :param appid: 应用ID
    :return: dict 或 None
    """
    record = session.query(AppToken).filter(AppToken.appid == appid).first()
    if not record:
        return None

    now = datetime.now(timezone.utc)
    elapsed = (now - record.updated_at).total_seconds()

    expires_in = max(0, record.expires_in - int(elapsed))
    refresh_expires_in = max(0, record.refresh_token_expires_in - int(elapsed))

    return {
        "id": record.id,
        "username": record.username,
        "userid": record.userid,
        "appid": record.appid,
        "access_token": record.access_token,
        "expires_in": expires_in,
        "refresh_token": record.refresh_token,
        "refresh_token_expires_in": refresh_expires_in,
        "updated_at": record.updated_at,
    }


def insert_api_call_log(session: Session, caller: str, caller_ip: str) -> bool:
    """
    插入一条 API 调用日志
    :param session: Session 数据库会话
    :param caller: 调用人
    :param caller_ip: 调用者IP
    :return: 是否成功
    """

    new_log = ApiCallLog(caller=caller, caller_ip=caller_ip)
    session.add(new_log)
    try:
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False