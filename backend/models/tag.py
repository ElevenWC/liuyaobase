"""标签表（二级标签，parent_id 自引用）+ 卦例-标签关联表"""
from typing import List, Optional
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class GualiTag(SQLModel, table=True):
    """卦例-标签关联表（纯关联，不建独立文件）"""
    __tablename__ = "guali_tag"
    guali_id: int = Field(foreign_key="guali.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    name: str = Field(max_length=50)
    is_system: bool = Field(default=False)
    sort_order: int = Field(default=0)

    parent: Mapped[Optional["Tag"]] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "tag.c.id"},
    )
    children: Mapped[List["Tag"]] = Relationship(back_populates="parent")
    gualis: Mapped[List["Guali"]] = Relationship(
        back_populates="tags",
        link_model=GualiTag,
    )
