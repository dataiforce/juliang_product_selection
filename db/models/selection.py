from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime, Text
import datetime
import pytz
from db.models.base import Base


class PromotionProduct(Base):
    __tablename__ = "promotion_product"

    promotion_id = Column(String, primary_key=True, index=True, comment="推广ID")
    aweme_id = Column(String, comment="抖音ID")
    cover_url = Column(String, comment="封面链接")
    image_list = Column(String, comment="图片列表")
    account_phone = Column(String, comment="账号手机号")
    product_id = Column(String, comment="商品ID")
    product_title = Column(String, comment="商品名称")
    product_price = Column(Integer, comment="到手价，单位为分（使用需要*0.01）")
    product_cos = Column(Integer, comment="佣金，单位为分（使用需要*0.01）")
    good_ratio =  Column(Float, comment="好评率（百分比小数）")
    product_sales = Column(Integer, comment="已售")
    product_match = Column(Integer, comment="带货人数")
    shop_id = Column(String, comment="店铺ID")
    shop_name = Column(String, comment="店铺名称")
    exper_score = Column(String, comment="店铺综合得分")
    goods_score = Column(String, comment="商品分")
    logistics_score = Column(String, comment="物流分")
    service_score = Column(String, comment="商家分")
    sales_amount = Column(Integer, comment="总销售额，单位为分（使用需要*0.01）")
    sales = Column(Integer, comment="总销量")
    match_order_num = Column(Integer, comment="出单达人数")
    sales_content_num = Column(Integer, comment="出单内容数")
    format_order_conversion_rate = Column(String, comment="下单转化率")
    pv = Column(Integer, comment="浏览量")
    author_sale_per = Column(Integer, comment="达人推广占比")
    shop_sale_per = Column(Integer, comment="商家自卖占比")
    live_sale_per = Column(Integer, comment="直播销售占比")
    video_sale_per = Column(Integer, comment="视频销售占比")
    visuals_sale_per = Column(Integer, comment="图文销售占比")
    shopwindow_sale_per = Column(Integer, comment="橱窗销售占比")
    is_pass = Column(Boolean, comment="是否通过筛选")
    category = Column(String, comment="商品类别")
    roi_check = Column(Integer, comment="roi检查字段，0为未检查，1为检测中，2为检测通过，3为检测不通过，4为出现错误")
    roi = Column(Float, comment="手机端获取的roi数据")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), comment="记录创建时间")

    

    


class SaleContent(Base):
    __tablename__ = "sale_content"

    content_id = Column(String, primary_key=True, index=True, comment="内容唯一ID")
    promotion_id = Column(String, comment="推广ID")
    content_type = Column(String, comment="内容类型（视频、图文等）")
    content_title = Column(String, comment="内容标题")
    content_cover = Column(String, comment="内容封面图")

    video_url = Column(String, comment="视频链接")
    duration = Column(Integer, comment="视频时长（秒）")
    cover_url = Column(String, comment="视频封面图链接")

    publish_time = Column(DateTime, comment="发布时间")

    author_name = Column(String, comment="作者昵称")
    author_avatar = Column(String, comment="作者头像链接")
    author_sec_id = Column(String, comment="作者的sec_id")
    author_level = Column(Integer, comment="作者等级")
    author_fans_count = Column(Integer, comment="粉丝数")
    author_resident = Column(String, comment="作者常驻地")
    share_url = Column(String, comment="视频分享链接")

    sales = Column(Integer, comment="销量")
    format_sales = Column(String, comment="格式化销量（带单位）")
    sales_amount = Column(BigInteger, comment="销售额（分）")
    format_sales_amount = Column(String, comment="格式化销售额（带单位）")

    like_count = Column(Integer, comment="点赞数")
    play_count = Column(BigInteger, comment="播放量")
    order_conversion_rate = Column(Float, comment="下单转化率（百分比小数）")
    format_order_conversion_rate = Column(String, comment="格式化下单转化率（带百分号）")
    click_rate = Column(Float, comment="点击率（百分比小数）")
    comment_count = Column(Integer, comment="评论数")
    share_count = Column(Integer, comment="分享数")
    pcu = Column(Integer, comment="同时在线人数峰值")
    is_self_sale = Column(Boolean, comment="是否为自卖")
    is_download = Column(Boolean, default=False, comment="该视频是否下载过")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(pytz.timezone("Asia/Shanghai")), comment="记录创建时间")


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


