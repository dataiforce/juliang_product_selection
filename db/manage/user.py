from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from db.models.user import DouyinAccount

def insert_douyin_account(session: Session,
                           aweme_id: str,
                           qianchuan_id: Optional[str] = None,
                           baiying_id: Optional[str] = None,
                           iphone: Optional[str] = None,
                           nickname: Optional[str] = None,
                           password: Optional[str] = None,
                           cooperation_code: Optional[str] = None,
                           create_at: Optional[datetime] = None,
                           binding_time: Optional[datetime] = None,
                           comment: Optional[str] = None,
                           account_status: int = 1) -> DouyinAccount:
    """
    插入一条抖音账号记录，account_status 默认为1
    """
    obj = DouyinAccount(
        aweme_id=aweme_id,
        qianchuan_id=qianchuan_id,
        baiying_id=baiying_id,
        iphone=iphone,
        nickname=nickname,
        password=password,
        cooperation_code=cooperation_code,
        create_at=create_at,
        binding_time=binding_time,
        account_status=account_status,
        account_status_modification_time=datetime.utcnow(),
        comment=comment
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def get_douyin_account(session: Session,
                       aweme_id: Optional[str] = None,
                       qianchuan_id: Optional[str] = None,
                       baiying_id: Optional[str] = None) -> Optional[DouyinAccount]:
    """
    查询一条账号记录，可通过 aweme_id 或 qianchuan_id 或 baiying_id 限制
    """
    if not any([aweme_id, qianchuan_id, baiying_id]):
        raise ValueError("至少提供一个 ID 进行查询")

    query = select(DouyinAccount)
    if aweme_id:
        query = query.where(DouyinAccount.aweme_id == aweme_id)
    if qianchuan_id:
        query = query.where(DouyinAccount.qianchuan_id == qianchuan_id)
    if baiying_id:
        query = query.where(DouyinAccount.baiying_id == baiying_id)

    result = session.execute(query).scalars().first()
    return result


def update_account_status(session: Session,
                          new_status: int,
                          aweme_id: Optional[str] = None,
                          qianchuan_id: Optional[str] = None,
                          baiying_id: Optional[str] = None) -> int:
    """
    修改账号状态，通过 aweme_id 或 qianchuan_id 或 baiying_id 限制
    返回受影响行数
    """
    if not any([aweme_id, qianchuan_id, baiying_id]):
        raise ValueError("至少提供一个 ID 进行更新")

    query = update(DouyinAccount).values(
        account_status=new_status,
        account_status_modification_time=datetime.utcnow()
    )
    if aweme_id:
        query = query.where(DouyinAccount.aweme_id == aweme_id)
    if qianchuan_id:
        query = query.where(DouyinAccount.qianchuan_id == qianchuan_id)
    if baiying_id:
        query = query.where(DouyinAccount.baiying_id == baiying_id)

    result = session.execute(query)
    session.commit()
    return result.rowcount
