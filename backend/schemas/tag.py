"""标签请求/响应 Schema"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class TagCreateRequest(BaseModel):
    name: str
    parent_id: Optional[int] = None


class TagUpdateRequest(BaseModel):
    name: str


class TagTreeNode(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: list[TagTreeNode] = []
