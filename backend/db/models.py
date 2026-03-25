# -*- coding: utf-8 -*-
"""
六爻卦例分析系统 - 数据库ORM模型

定义数据库表的SQLAlchemy ORM模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from backend.db.connection import Base


class GualiModel(Base):
    """
    卦例表ORM模型

    存储卦例的基础信息和时间、卦象等编码数据
    """
    __tablename__ = 'guali'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='卦例ID')
    solar_year = Column(Integer, nullable=False, comment='公历年')
    solar_month = Column(Integer, nullable=False, comment='公历月')
    solar_day = Column(Integer, nullable=False, comment='公历日')
    ganzhi_year = Column(String(4), nullable=False, comment='年柱(干支)')
    ganzhi_month = Column(String(4), nullable=False, comment='月柱(干支)')
    ganzhi_day = Column(String(4), nullable=False, comment='日柱(干支)')
    xunkong = Column(String(8), nullable=False, comment='旬空')
    ben_gua_code = Column(Integer, nullable=False, comment='本卦代码(6位二进制转十进制)')
    zhi_gua_code = Column(Integer, nullable=True, comment='之卦代码(6位二进制转十进制)')
    yao_bian_code = Column(Integer, nullable=False, default=0, comment='爻变代码(6位二进制转十进制)')
    gongwei = Column(String(8), nullable=False, comment='卦宫')
    gongwei_index = Column(String(8), nullable=False, comment='宫位')
    zhan_wen = Column(Text, nullable=True, comment='占问事由')
    zhan_duan = Column(Text, nullable=True, comment='占断')
    image_path = Column(String(512), nullable=True, comment='图片路径')
    created_at = Column(TIMESTAMP, default=datetime.now, comment='创建时间')
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系：一个卦例有六个爻详情
    yao_details = relationship("YaoDetailModel", back_populates="guali", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GualiModel(id={self.id}, ben_gua_code={self.ben_gua_code}, " \
               f"solar_date={self.solar_year}/{self.solar_month}/{self.solar_day})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'solar_year': self.solar_year,
            'solar_month': self.solar_month,
            'solar_day': self.solar_day,
            'ganzhi_year': self.ganzhi_year,
            'ganzhi_month': self.ganzhi_month,
            'ganzhi_day': self.ganzhi_day,
            'xunkong': self.xunkong,
            'ben_gua_code': self.ben_gua_code,
            'zhi_gua_code': self.zhi_gua_code,
            'yao_bian_code': self.yao_bian_code,
            'gongwei': self.gongwei,
            'gongwei_index': self.gongwei_index,
            'zhan_wen': self.zhan_wen,
            'zhan_duan': self.zhan_duan,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class YaoDetailModel(Base):
    """
    爻详情表ORM模型

    存储卦例中每个爻的详细信息
    """
    __tablename__ = 'yao_detail'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='爻详情ID')
    guali_id = Column(Integer, ForeignKey('guali.id', ondelete='CASCADE'), nullable=False, comment='卦例ID')
    position = Column(Integer, nullable=False, comment='爻位(1-6: 初爻到上爻)')
    yao_type = Column(Integer, nullable=False, comment='爻类型(1=阳爻, 0=阴爻)')
    state = Column(Integer, nullable=False, default=0, comment='爻状态(1=动爻, 0=静爻)')
    dizhi = Column(String(4), nullable=False, comment='地支')
    liuqin = Column(String(8), nullable=True, comment='六亲')
    liushen = Column(String(8), nullable=True, comment='六神')
    is_world = Column(Boolean, default=False, comment='是否世爻')
    is_response = Column(Boolean, default=False, comment='是否应爻')
    created_at = Column(TIMESTAMP, default=datetime.now, comment='创建时间')

    # 关系：多个爻属于一个卦例
    guali = relationship("GualiModel", back_populates="yao_details")

    def __repr__(self):
        return f"<YaoDetailModel(id={self.id}, guali_id={self.guali_id}, " \
               f"position={self.position}, dizhi={self.dizhi})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'guali_id': self.guali_id,
            'position': self.position,
            'yao_type': self.yao_type,
            'state': self.state,
            'dizhi': self.dizhi,
            'liuqin': self.liuqin,
            'liushen': self.liushen,
            'is_world': self.is_world,
            'is_response': self.is_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class YanqingModel(Base):
    """
    占验情况表ORM模型

    独立于主数据库的弱耦合系统，存储卦例的占验情况标注
    """
    __tablename__ = 'yanqing'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='占验ID')
    guali_id = Column(Integer, unique=True, nullable=False, comment='卦例ID')
    status = Column(String(8), nullable=False, comment='占验状态(应验/模糊/不验)')
    note = Column(Text, nullable=True, comment='标注说明')
    annotated_at = Column(TIMESTAMP, default=datetime.now, comment='标注时间')
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<YanqingModel(id={self.id}, guali_id={self.guali_id}, status={self.status})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'guali_id': self.guali_id,
            'status': self.status,
            'note': self.note,
            'annotated_at': self.annotated_at.isoformat() if self.annotated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
