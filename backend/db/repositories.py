# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 数据仓库模块

本模块实现卦例和爻详情的数据库CRUD操作
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db.connection import get_session
from backend.db.models import GualiModel, YaoDetailModel, YanqingModel
from backend.core.models import Guali, Yao
from backend.core.enums import ZhongGua, Dizhi, LiuQin, LiuShen


class GualiRepository:
    """
    卦例数据仓库

    实现卦例的CRUD操作，以及与业务对象Guali的相互转换
    """

    # =========================================================================
    # 创建操作
    # =========================================================================

    def create_guali(
        self,
        solar_year: int,
        solar_month: int,
        solar_day: int,
        ganzhi_year: str,
        ganzhi_month: str,
        ganzhi_day: str,
        xunkong: str,
        ben_gua_code: int,
        zhi_gua_code: Optional[int] = None,
        yao_bian_code: int = 0,
        gongwei: str = "",
        gongwei_index: str = "",
        zhan_wen: Optional[str] = None,
        zhan_duan: Optional[str] = None,
        image_path: Optional[str] = None,
        session: Optional[Session] = None
    ) -> GualiModel:
        """
        创建卦例记录

        Args:
            solar_year: 公历年
            solar_month: 公历月
            solar_day: 公历日
            ganzhi_year: 年柱干支
            ganzhi_month: 月柱干支
            ganzhi_day: 日柱干支
            xunkong: 旬空
            ben_gua_code: 本卦代码
            zhi_gua_code: 之卦代码（可选）
            yao_bian_code: 爻变代码
            gongwei: 卦宫
            gongwei_index: 宫位
            zhan_wen: 占问事由
            zhan_duan: 占断
            image_path: 图片路径
            session: 数据库会话（可选，不提供则创建新会话）

        Returns:
            创建的卦例模型对象
        """
        guali_model = GualiModel(
            solar_year=solar_year,
            solar_month=solar_month,
            solar_day=solar_day,
            ganzhi_year=ganzhi_year,
            ganzhi_month=ganzhi_month,
            ganzhi_day=ganzhi_day,
            xunkong=xunkong,
            ben_gua_code=ben_gua_code,
            zhi_gua_code=zhi_gua_code,
            yao_bian_code=yao_bian_code,
            gongwei=gongwei,
            gongwei_index=gongwei_index,
            zhan_wen=zhan_wen,
            zhan_duan=zhan_duan,
            image_path=image_path
        )

        if session:
            session.add(guali_model)
            session.flush()  # 获取自增ID
        else:
            with get_session() as sess:
                sess.add(guali_model)
                sess.flush()
                sess.expunge(guali_model)  # 从会话分离

        return guali_model

    def create_from_guali(self, guali: Guali, session: Optional[Session] = None) -> GualiModel:
        """
        从业务对象Guali创建数据库记录

        Args:
            guali: 卦例业务对象
            session: 数据库会话（可选）

        Returns:
            创建的卦例模型对象
        """
        return self.create_guali(
            solar_year=guali.solar_year,
            solar_month=guali.solar_month,
            solar_day=guali.solar_day,
            ganzhi_year=guali.ganzhi_year or "",
            ganzhi_month=guali.ganzhi_month or "",
            ganzhi_day=guali.ganzhi_day or "",
            xunkong=guali.xunkong or "",
            ben_gua_code=guali.ben_gua_code,
            zhi_gua_code=guali.zhi_gua_code if guali.zhi_gua else None,
            yao_bian_code=guali.yao_bian_code,
            gongwei=guali.gongwei or "",
            gongwei_index=guali.gongwei_index or "",
            zhan_wen=guali.zhan_wen,
            zhan_duan=guali.zhan_duan,
            image_path=guali.image_path,
            session=session
        )

    # =========================================================================
    # 查询操作
    # =========================================================================

    def get_guali_by_id(self, guali_id: int, session: Optional[Session] = None) -> Optional[GualiModel]:
        """
        根据ID获取卦例

        Args:
            guali_id: 卦例ID
            session: 数据库会话（可选）

        Returns:
            卦例模型对象，不存在则返回None
        """
        if session:
            return session.query(GualiModel).filter(GualiModel.id == guali_id).first()
        else:
            with get_session() as sess:
                guali = sess.query(GualiModel).filter(GualiModel.id == guali_id).first()
                if guali:
                    sess.expunge(guali)
                return guali

    def get_all_gualis(
        self,
        page: int = 1,
        page_size: int = 20,
        session: Optional[Session] = None
    ) -> Tuple[List[GualiModel], int]:
        """
        获取所有卦例（分页）

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            session: 数据库会话（可选）

        Returns:
            (卦例列表, 总数)
        """
        offset = (page - 1) * page_size

        if session:
            total = session.query(GualiModel).count()
            gualis = session.query(GualiModel) \
                .order_by(GualiModel.id.desc()) \
                .offset(offset) \
                .limit(page_size) \
                .all()
            return gualis, total
        else:
            with get_session() as sess:
                total = sess.query(GualiModel).count()
                gualis = sess.query(GualiModel) \
                    .order_by(GualiModel.id.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()
                for g in gualis:
                    sess.expunge(g)
                return gualis, total

    def get_gualis_by_year(
        self,
        year: int,
        page: int = 1,
        page_size: int = 20,
        session: Optional[Session] = None
    ) -> Tuple[List[GualiModel], int]:
        """
        根据公历年份获取卦例

        Args:
            year: 公历年
            page: 页码
            page_size: 每页数量
            session: 数据库会话（可选）

        Returns:
            (卦例列表, 总数)
        """
        offset = (page - 1) * page_size

        if session:
            query = session.query(GualiModel).filter(GualiModel.solar_year == year)
            total = query.count()
            gualis = query.order_by(GualiModel.id.desc()) \
                .offset(offset) \
                .limit(page_size) \
                .all()
            return gualis, total
        else:
            with get_session() as sess:
                query = sess.query(GualiModel).filter(GualiModel.solar_year == year)
                total = query.count()
                gualis = query.order_by(GualiModel.id.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()
                for g in gualis:
                    sess.expunge(g)
                return gualis, total

    def get_gualis_by_gongwei(
        self,
        gongwei: str,
        page: int = 1,
        page_size: int = 20,
        session: Optional[Session] = None
    ) -> Tuple[List[GualiModel], int]:
        """
        根据卦宫获取卦例

        Args:
            gongwei: 卦宫名称
            page: 页码
            page_size: 每页数量
            session: 数据库会话（可选）

        Returns:
            (卦例列表, 总数)
        """
        offset = (page - 1) * page_size

        if session:
            query = session.query(GualiModel).filter(GualiModel.gongwei == gongwei)
            total = query.count()
            gualis = query.order_by(GualiModel.id.desc()) \
                .offset(offset) \
                .limit(page_size) \
                .all()
            return gualis, total
        else:
            with get_session() as sess:
                query = sess.query(GualiModel).filter(GualiModel.gongwei == gongwei)
                total = query.count()
                gualis = query.order_by(GualiModel.id.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()
                for g in gualis:
                    sess.expunge(g)
                return gualis, total

    def search_gualis(
        self,
        ben_gua_name: Optional[str] = None,
        zhi_gua_name: Optional[str] = None,
        zhan_wen_keyword: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        session: Optional[Session] = None
    ) -> Tuple[List[GualiModel], int]:
        """
        搜索卦例

        Args:
            ben_gua_name: 本卦名
            zhi_gua_name: 之卦名
            zhan_wen_keyword: 占问事由关键词
            year: 公历年
            month: 公历月
            day: 公历日
            page: 页码
            page_size: 每页数量
            session: 数据库会话（可选）

        Returns:
            (卦例列表, 总数)
        """
        offset = (page - 1) * page_size

        def do_query(sess: Session):
            query = sess.query(GualiModel)

            # 根据本卦名筛选
            if ben_gua_name:
                ben_gua = ZhongGua.from_name(ben_gua_name)
                if ben_gua:
                    query = query.filter(GualiModel.ben_gua_code == ben_gua.code)

            # 根据之卦名筛选
            if zhi_gua_name:
                zhi_gua = ZhongGua.from_name(zhi_gua_name)
                if zhi_gua:
                    query = query.filter(GualiModel.zhi_gua_code == zhi_gua.code)

            # 根据占问事由关键词筛选
            if zhan_wen_keyword:
                query = query.filter(GualiModel.zhan_wen.like(f"%{zhan_wen_keyword}%"))

            # 根据日期筛选
            if year is not None:
                query = query.filter(GualiModel.solar_year == year)
            if month is not None:
                query = query.filter(GualiModel.solar_month == month)
            if day is not None:
                query = query.filter(GualiModel.solar_day == day)

            total = query.count()
            gualis = query.order_by(GualiModel.id.desc()) \
                .offset(offset) \
                .limit(page_size) \
                .all()

            return gualis, total

        if session:
            return do_query(session)
        else:
            with get_session() as sess:
                gualis, total = do_query(sess)
                for g in gualis:
                    sess.expunge(g)
                return gualis, total

    # =========================================================================
    # 更新操作
    # =========================================================================

    def update_guali(
        self,
        guali_id: int,
        zhan_wen: Optional[str] = None,
        zhan_duan: Optional[str] = None,
        image_path: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Optional[GualiModel]:
        """
        更新卦例（只允许更新语句字段和图片路径）

        注意：时间和卦象字段不允许修改，只允许更新语句字段

        Args:
            guali_id: 卦例ID
            zhan_wen: 新的占问事由
            zhan_duan: 新的占断
            image_path: 新的图片路径
            session: 数据库会话（可选）

        Returns:
            更新后的卦例模型对象，不存在则返回None
        """
        def do_update(sess: Session):
            guali = sess.query(GualiModel).filter(GualiModel.id == guali_id).first()
            if not guali:
                return None

            if zhan_wen is not None:
                guali.zhan_wen = zhan_wen
            if zhan_duan is not None:
                guali.zhan_duan = zhan_duan
            if image_path is not None:
                guali.image_path = image_path

            sess.flush()
            return guali

        if session:
            return do_update(session)
        else:
            with get_session() as sess:
                guali = do_update(sess)
                if guali:
                    sess.expunge(guali)
                return guali

    # =========================================================================
    # 删除操作
    # =========================================================================

    def delete_guali(self, guali_id: int, session: Optional[Session] = None) -> bool:
        """
        删除卦例

        同时会级联删除关联的爻详情

        Args:
            guali_id: 卦例ID
            session: 数据库会话（可选）

        Returns:
            删除成功返回True，不存在返回False
        """
        def do_delete(sess: Session):
            guali = sess.query(GualiModel).filter(GualiModel.id == guali_id).first()
            if not guali:
                return False

            sess.delete(guali)
            return True

        if session:
            return do_delete(session)
        else:
            with get_session() as sess:
                return do_delete(sess)

    # =========================================================================
    # 转换方法
    # =========================================================================

    def model_to_guali(self, model: GualiModel, with_yao_details: bool = True) -> Guali:
        """
        将数据库模型转换为业务对象

        Args:
            model: 数据库模型
            with_yao_details: 是否加载爻详情

        Returns:
            卦例业务对象
        """
        # 获取本卦和之卦
        ben_gua = ZhongGua.from_code(model.ben_gua_code)
        zhi_gua = ZhongGua.from_code(model.zhi_gua_code) if model.zhi_gua_code else None

        guali = Guali(
            id=model.id,
            solar_year=model.solar_year,
            solar_month=model.solar_month,
            solar_day=model.solar_day,
            ganzhi_year=model.ganzhi_year,
            ganzhi_month=model.ganzhi_month,
            ganzhi_day=model.ganzhi_day,
            xunkong=model.xunkong,
            ben_gua=ben_gua,
            zhi_gua=zhi_gua,
            yao_bian_code=model.yao_bian_code,
            zhan_wen=model.zhan_wen,
            zhan_duan=model.zhan_duan,
            image_path=model.image_path
        )

        # 如果需要加载爻详情
        if with_yao_details and model.yao_details:
            guali.yaos = []
            for yao_model in sorted(model.yao_details, key=lambda y: y.position):
                yao = Yao(
                    position=yao_model.position,
                    yao_type=yao_model.yao_type,
                    state=yao_model.state,
                    dizhi=Dizhi.from_char(yao_model.dizhi) if yao_model.dizhi else None,
                    liuqin=LiuQin(yao_model.liuqin) if yao_model.liuqin else None,
                    liushen=LiuShen(yao_model.liushen) if yao_model.liushen else None,
                    is_world=yao_model.is_world,
                    is_response=yao_model.is_response
                )
                guali.yaos.append(yao)

        return guali


class YaoDetailRepository:
    """
    爻详情数据仓库

    实现爻详情的CRUD操作
    """

    def save_yao_details(
        self,
        guali_id: int,
        yaos: List[Yao],
        session: Optional[Session] = None
    ) -> List[YaoDetailModel]:
        """
        批量保存爻详情

        先删除已有的爻详情，再插入新的

        Args:
            guali_id: 卦例ID
            yaos: 爻业务对象列表
            session: 数据库会话（可选）

        Returns:
            创建的爻详情模型列表
        """
        def do_save(sess: Session):
            # 先删除已有的爻详情
            sess.query(YaoDetailModel).filter(YaoDetailModel.guali_id == guali_id).delete()

            # 创建新的爻详情
            yao_models = []
            for yao in yaos:
                yao_model = YaoDetailModel(
                    guali_id=guali_id,
                    position=yao.position,
                    yao_type=yao.yao_type,
                    state=yao.state,
                    dizhi=yao.dizhi.value if yao.dizhi else "",
                    liuqin=yao.liuqin.value if yao.liuqin else None,
                    liushen=yao.liushen.value if yao.liushen else None,
                    is_world=yao.is_world,
                    is_response=yao.is_response
                )
                sess.add(yao_model)
                yao_models.append(yao_model)

            sess.flush()
            return yao_models

        if session:
            return do_save(session)
        else:
            with get_session() as sess:
                yao_models = do_save(sess)
                for ym in yao_models:
                    sess.expunge(ym)
                return yao_models

    def get_yao_details(self, guali_id: int, session: Optional[Session] = None) -> List[YaoDetailModel]:
        """
        获取卦例的爻详情列表

        Args:
            guali_id: 卦例ID
            session: 数据库会话（可选）

        Returns:
            爻详情模型列表
        """
        if session:
            return session.query(YaoDetailModel) \
                .filter(YaoDetailModel.guali_id == guali_id) \
                .order_by(YaoDetailModel.position) \
                .all()
        else:
            with get_session() as sess:
                yao_models = sess.query(YaoDetailModel) \
                    .filter(YaoDetailModel.guali_id == guali_id) \
                    .order_by(YaoDetailModel.position) \
                    .all()
                for ym in yao_models:
                    sess.expunge(ym)
                return yao_models

    def get_yao_detail_by_position(
        self,
        guali_id: int,
        position: int,
        session: Optional[Session] = None
    ) -> Optional[YaoDetailModel]:
        """
        获取指定位置的爻详情

        Args:
            guali_id: 卦例ID
            position: 爻位 (1-6)
            session: 数据库会话（可选）

        Returns:
            爻详情模型对象，不存在则返回None
        """
        if session:
            return session.query(YaoDetailModel) \
                .filter(YaoDetailModel.guali_id == guali_id) \
                .filter(YaoDetailModel.position == position) \
                .first()
        else:
            with get_session() as sess:
                yao_model = sess.query(YaoDetailModel) \
                    .filter(YaoDetailModel.guali_id == guali_id) \
                    .filter(YaoDetailModel.position == position) \
                    .first()
                if yao_model:
                    sess.expunge(yao_model)
                return yao_model


class YanqingRepository:
    """
    占验情况数据仓库

    实现占验情况的CRUD操作
    """

    def annotate(
        self,
        guali_id: int,
        status: str,
        note: Optional[str] = None,
        session: Optional[Session] = None
    ) -> YanqingModel:
        """
        标注占验情况

        如果已存在则更新，否则创建新记录

        Args:
            guali_id: 卦例ID
            status: 占验状态（应验/模糊/不验）
            note: 标注说明
            session: 数据库会话（可选）

        Returns:
            占验情况模型对象
        """
        def do_annotate(sess: Session):
            existing = sess.query(YanqingModel).filter(YanqingModel.guali_id == guali_id).first()

            if existing:
                existing.status = status
                existing.note = note
                existing.updated_at = datetime.now()
                sess.flush()
                return existing
            else:
                yanqing = YanqingModel(
                    guali_id=guali_id,
                    status=status,
                    note=note
                )
                sess.add(yanqing)
                sess.flush()
                return yanqing

        if session:
            return do_annotate(session)
        else:
            with get_session() as sess:
                yanqing = do_annotate(sess)
                sess.expunge(yanqing)
                return yanqing

    def get_by_guali_id(self, guali_id: int, session: Optional[Session] = None) -> Optional[YanqingModel]:
        """
        根据卦例ID获取占验情况

        Args:
            guali_id: 卦例ID
            session: 数据库会话（可选）

        Returns:
            占验情况模型对象，不存在则返回None
        """
        if session:
            return session.query(YanqingModel).filter(YanqingModel.guali_id == guali_id).first()
        else:
            with get_session() as sess:
                yanqing = sess.query(YanqingModel).filter(YanqingModel.guali_id == guali_id).first()
                if yanqing:
                    sess.expunge(yanqing)
                return yanqing

    def delete_by_guali_id(self, guali_id: int, session: Optional[Session] = None) -> bool:
        """
        删除占验情况

        Args:
            guali_id: 卦例ID
            session: 数据库会话（可选）

        Returns:
            删除成功返回True，不存在返回False
        """
        def do_delete(sess: Session):
            yanqing = sess.query(YanqingModel).filter(YanqingModel.guali_id == guali_id).first()
            if not yanqing:
                return False
            sess.delete(yanqing)
            return True

        if session:
            return do_delete(session)
        else:
            with get_session() as sess:
                return do_delete(sess)

    def get_all_by_status(
        self,
        status: str,
        page: int = 1,
        page_size: int = 20,
        session: Optional[Session] = None
    ) -> Tuple[List[YanqingModel], int]:
        """
        根据占验状态获取列表

        Args:
            status: 占验状态
            page: 页码
            page_size: 每页数量
            session: 数据库会话（可选）

        Returns:
            (占验情况列表, 总数)
        """
        offset = (page - 1) * page_size

        if session:
            query = session.query(YanqingModel).filter(YanqingModel.status == status)
            total = query.count()
            yanqings = query.order_by(YanqingModel.annotated_at.desc()) \
                .offset(offset) \
                .limit(page_size) \
                .all()
            return yanqings, total
        else:
            with get_session() as sess:
                query = sess.query(YanqingModel).filter(YanqingModel.status == status)
                total = query.count()
                yanqings = query.order_by(YanqingModel.annotated_at.desc()) \
                    .offset(offset) \
                    .limit(page_size) \
                    .all()
                for y in yanqings:
                    sess.expunge(y)
                return yanqings, total


# 创建全局仓库实例
guali_repository = GualiRepository()
yao_detail_repository = YaoDetailRepository()
yanqing_repository = YanqingRepository()
