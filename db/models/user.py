from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from db.models.base import Base

class DouyinAccount(Base):
    __tablename__ = "douyin_account"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增ID")
    aweme_id = Column(String, comment="抖音ID")
    qianchuan_id = Column(String, comment="千川广告主ID")
    baiying_id = Column(String, comment="百应选品平台ID")
    iphone = Column(String, comment="绑定手机手机号")
    nickname = Column(String, comment="抖音昵称")
    password = Column(String, comment="抖音登录密码")
    cooperation_code = Column(String, comment="合作码")
    create_at = Column(DateTime(timezone=True), comment="抖音号创建时间")
    binding_time = Column(DateTime(timezone=True), comment="绑定选品平台的时间")
    account_status = Column(Integer, comment="账号状态: 0:不可用; 1:可用; 2:解绑; 3:封禁")
    account_status_modification_time = Column(DateTime(timezone=True), comment="账号状态修改时间")
    comment = Column(String, comment="备注")
