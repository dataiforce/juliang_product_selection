from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime, Text
import datetime
import pytz
from db.models.base import Base

class Material(Base):
    __tablename__ = "material"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    aweme_id = Column(String, comment="抖音ID")
    video_cover_id = Column(String, comment="视频封面ID")
    promotion_card_image_id = Column(String, comment="推广卡图片ID")
    advertiser_id = Column(String, comment="广告主ID")
    promotion_id = Column(String, index=True, comment="推广ID")
    product_id = Column(String, comment="商品ID")
    qianchuan_id = Column(String, comment="千川ID")
    video_id = Column(String, comment="我们上传的视频ID")
    shop_id = Column(String, comment="店铺ID")
    shop_name = Column(String, comment="店铺名称")
    content_id = Column(String, unique=True, index=True,comment="视频的唯一ID")
    video_path = Column(String, comment="视频路径")
    video_name = Column(String, comment="视频名称")
    usable = Column(Boolean ,default=False, comment="该素材是否可以使用")
    is_aigc = Column(Boolean, default=False, comment="是否AIGC生成")
    use_status = Column(Boolean, default=False, comment="该素材是否被使用")
    is_qianchuan = Column(Integer, comment="是否为千川素材 可选:0-千川图文;1-千川视频;2-达人图文;3-达人视频")
    hide_in_aweme = Column(Boolean, default=True, comment="抖音主页可见性设置")
    use_at = Column(DateTime(timezone=True), comment="使用时间")
    is_vertica = Column(Boolean, comment="是否为竖屏视频")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), comment="创建时间")


