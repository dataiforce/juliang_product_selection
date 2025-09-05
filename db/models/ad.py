from sqlalchemy import Column, String, Integer, Float, DateTime, Text
import datetime
import pytz
from db.models.base import Base


class AdPlan(Base):
    __tablename__ = "ad_plan"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    ad_id = Column(String, index=True, comment="全域商品推广计划ID")
    advertiser_id = Column(String, comment="广告主ID")
    name = Column(String, comment="推广计划名称")
    aweme_id = Column(String, comment="抖音ID")
    marketing_goal = Column(String, comment="营销目标")
    raw_data = Column(Text, comment="序列化后原始数据json")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), comment="创建时间")


class AdPlanUpdateHistory(Base):
    __tablename__ = "regulation_record"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键自增ID")
    advertiser_id = Column(String, nullable=False, comment="千川ID(必填)")
    ad_id = Column(String, nullable=False, comment="广告主ID(必填)")
    name = Column(String, nullable=True, comment="更新的计划名称，默认 null")
    budget = Column(Float, nullable=True, comment="更新后的预算，单位元，最多支持两位小数")
    roi2_goal = Column(Float, nullable=True, comment="ROI2 目标，最多支持两位小数")
    regulation_json = Column(Text, nullable=False, comment="调控的json字符串(必填)")
    response_json = Column(Text, nullable=False, comment="请求响应的json字符串 (必填)")
    opt_status = Column(String , nullable=True, comment="更新推广计划状态，['DISABLE, ENABLE, DELETE']")
    modifier = Column(String, nullable=False, comment="修改人(必填)")
    regulation_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), nullable=False, comment="调控记录时间")
