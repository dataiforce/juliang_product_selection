from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from db.models.selection import PromotionProduct, SaleContent, Material
from sqlalchemy import select
import datetime
from sqlalchemy import inspect
from typing import Optional
from sqlalchemy import update



def insert_promotion_product(session: Session, data: dict) -> PromotionProduct:
    """
    向 promotion_product 表插入一条记录
    :param session: SQLAlchemy Session
    :param data: 字段字典，键为列名
    :return: 新插入的 PromotionProduct 对象
    """
    try:
        obj = PromotionProduct(
            created_at=datetime.datetime.utcnow(),
            **data
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except SQLAlchemyError as e:
        print(f"SQL 错误：{e.orig if hasattr(e, 'orig') else str(e)}")
        session.rollback()
        return None

def insert_sale_content(session: Session, data: dict) -> SaleContent:
    """
    向 sale_content 表插入一条记录
    :param session: SQLAlchemy Session
    :param data: 字段字典，键为列名
    :return: 新插入的 SaleContent 对象
    """
    try:
        obj = SaleContent(
            created_at=datetime.datetime.utcnow(),
            **data
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except SQLAlchemyError as e:
        print(f"SQL 错误：{e.orig if hasattr(e, 'orig') else str(e)}")
        session.rollback()
        return None
    

def promotion_exists(session: Session, promotion_id: str) -> bool:
    """
    检查 promotion_id 是否存在于 promotion_product 表中
    """
    stmt = select(PromotionProduct).where(PromotionProduct.promotion_id == promotion_id)
    result = session.execute(stmt).first()
    return result is not None


def get_promotion_product_by_id(session: Session, promotion_id: str):
    return session.get(PromotionProduct, promotion_id)



def get_unprocessed_promotion(session: Session):
    """
    获取 roi_check 状态为0（未检查）且 is_pass 为 True 的 PromotionProduct 记录，
    并尝试用竞争性更新（乐观锁）将状态改为1（检测中），
    成功则返回该记录，失败返回 None。
    """
    obj = session.query(PromotionProduct)\
                 .filter(PromotionProduct.roi_check == 0, PromotionProduct.is_pass == True)\
                 .first()
    if not obj:
        return None

    rows_updated = session.query(PromotionProduct)\
                          .filter_by(promotion_id=obj.promotion_id, roi_check=0, is_pass=True)\
                          .update({PromotionProduct.roi_check: 1})

    if rows_updated == 0:
        session.rollback()
        return None
    else:
        session.commit()
        obj_dict = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return obj_dict



def set_roi_check(session: Session, promotion_id: str, roi_status: int, roi: Optional[float] = None):
    """
    修改指定 promotion_id 的 roi_check 状态为 roi_status。
    :param session: SQLAlchemy Session
    :param promotion_id: PromotionProduct 主键
    :param roi_status: 新的 roi_check 值（0~4）
    :param roi: 可选，新的 roi 值
    """
    obj = session.query(PromotionProduct).filter(PromotionProduct.promotion_id == promotion_id).first()
    if obj:
        obj.roi_check = roi_status
        if roi is not None:   # 只有传了才更新
            obj.roi = roi
        session.commit()
        return True
    return False


def insert_material(session: Session, data: dict) -> Material:
    """
    向 material 表插入一条记录
    :param session: SQLAlchemy Session
    :param data: 字段字典，键为列名
    :return: 新插入的 Material 对象
    """
    try:
        obj = Material(
            created_at=datetime.datetime.utcnow(),
            **data
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except SQLAlchemyError as e:
        print(f"SQL 错误：{e.orig if hasattr(e, 'orig') else str(e)}")
        session.rollback()
        return None


def get_material_by_content_id(session: Session, content_id: str):
    obj = session.query(Material).filter_by(content_id=content_id).first()
    obj_dict = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    return obj_dict


def set_usable_true(session: Session, content_id: str) -> dict | None:
    """
    根据 content_id 将 Material.usable 更新为 True，并返回该条记录的 dict
    :param session: Session
    :param content_id: str
    :return: dict | None
    """
    try:
        obj = session.query(Material).filter_by(content_id=content_id).first()
        if not obj:
            return None
        obj.usable = True
        session.commit()
        session.refresh(obj)  # 确保拿到最新值

        obj_dict = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return obj_dict
    except Exception:
        session.rollback()
        raise


def get_pending_download_contents_dict(session: Session):
    stmt = (
        select(
            SaleContent.content_id,
            SaleContent.content_title,
            SaleContent.content_type,
            SaleContent.promotion_id
        )
        .join(
            PromotionProduct,
            SaleContent.promotion_id == PromotionProduct.promotion_id
        )
        .where(
            SaleContent.is_download == False,
            PromotionProduct.is_pass == True
        )
    )
    result = session.execute(stmt)
    return [dict(row._mapping) for row in result]



def mark_content_downloaded(session: Session, content_id: str) -> bool:
    """
    根据 content_id 将 SaleContent.is_download 设置为 True
    :param session: SQLAlchemy Session
    :param content_id: SaleContent 主键
    :return: 是否成功更新
    """
    try:
        stmt = (
            update(SaleContent)
            .where(SaleContent.content_id == content_id)
            .values(is_download=True)
        )
        result = session.execute(stmt)
        session.commit()
        return result.rowcount > 0  # 更新到行返回 True
    except Exception as e:
        session.rollback()
        print(f"更新失败: {e}")
        return False


def mark_content_vertical(session: Session, content_id: str, is_vertical: bool) -> bool:
    """
    根据 content_id 更新 Material.is_vertica 字段为 True/False
    :param session: SQLAlchemy Session
    :param content_id: Material.content_id 主键
    :param is_vertical: 是否竖屏
    :return: 是否成功更新
    """
    try:
        stmt = (
            update(Material)
            .where(Material.content_id == content_id)
            .values(is_vertica=is_vertical)
        )
        result = session.execute(stmt)
        session.commit()
        return result.rowcount > 0  # 更新到行返回 True
    except Exception as e:
        session.rollback()
        print(f"更新失败: {e}")
        return False