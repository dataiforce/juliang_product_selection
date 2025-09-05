from sqlalchemy.orm import Session
from sqlalchemy import insert
import datetime, pytz
from typing import Dict, Optional
from db.models.ad import AdPlan, AdPlanUpdateHistory

def insert_ad_plan(session: Session, data: Dict) -> Optional[int]:
    """
    插入一条 AdPlan 记录
    :param session: Session
    :param data: dict
    :return: 插入的自增 id 或 None（失败）
    """
    try:
        stmt = insert(AdPlan).values(
            ad_id=data.get("ad_id"),
            advertiser_id=data.get("advertiser_id"),
            name=data.get("name"),
            aweme_id=data.get("aweme_id"),
            marketing_goal=data.get("marketing_goal"),
            raw_data=data.get("raw_data"),
            created_at=data.get(
                "created_at",
                datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
            )
        ).returning(AdPlan.id)

        result = session.execute(stmt)
        new_id = result.scalar_one()
        session.commit()
        return new_id

    except Exception as e:
        session.rollback()
        print(f"插入 AdPlan 失败: {e}")
        return None


def insert_ad_plan_update_history(session: Session, data: Dict) -> Optional[int]:
    """
    插入一条 AdPlanUpdateHistory 记录
    :param session: Session
    :param data: dict
    :return: 插入的自增 id 或 None（失败）
    """
    try:
        stmt = insert(AdPlanUpdateHistory).values(
            advertiser_id=data["advertiser_id"],
            ad_id=data["ad_id"],
            name=data.get("name"),
            budget=data.get("budget"),
            roi2_goal=data.get("roi2_goal"),
            regulation_json=data["regulation_json"],
            response_json=data["response_json"],
            opt_status=data.get("opt_status"),
            modifier=data["modifier"],
            regulation_at=data.get(
                "regulation_at",
                datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
            )
        ).returning(AdPlanUpdateHistory.id)

        result = session.execute(stmt)
        new_id = result.scalar_one()
        session.commit()
        return new_id

    except Exception as e:
        session.rollback()
        print(f"插入 AdPlanUpdateHistory 失败: {e}")
        return None