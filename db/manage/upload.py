import datetime
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from db.models.upload import Material

# 1. 根据 promotion_id 查询
def get_materials_by_promotion_id(db: Session, promotion_id: str):
    """
    查询满足指定 promotion_id 的所有 Material 记录
    """
    return db.query(Material).filter(Material.promotion_id == promotion_id, Material.usable.is_(True)).all()


# 2. 批量更新 use_status 和 use_at
def mark_materials_used(db: Session, promotion_id: str):
    """
    将满足指定 promotion_id 的所有记录 use_status 设为 True，
    并更新 use_at 时间戳
    """
    now = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
    db.query(Material).filter(Material.promotion_id == promotion_id).update(
        {
            Material.use_status: True,
            Material.use_at: now
        },
        synchronize_session=False
    )
    db.commit()


def update_material_video_info(db: Session, content_id: str, video_path: str, video_name: str):
    """
    根据 content_id 更新素材的视频路径和名称，并将 usable 设为 True
    """
    try:
        material = db.query(Material).filter(Material.content_id == content_id).one()
    except NoResultFound:
        return None  # 没有找到对应的记录
    
    material.video_path = video_path
    material.video_name = video_name
    material.usable = True
    material.created_at = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))  # 可选：如果需要刷新创建时间

    db.commit()
    db.refresh(material)
    return material

