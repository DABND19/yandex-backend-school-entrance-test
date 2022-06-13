from collections import defaultdict, deque
from datetime import datetime
from typing import (
    DefaultDict, Iterable, List, Optional
)
from uuid import UUID

from pydantic import validator

from src.db.models import ShopUnitType

from .base import BaseSchema, datetime_iso8601_validator


class BaseShopUnitSchema(BaseSchema):
    id: UUID
    name: str
    type: ShopUnitType
    parent_id: Optional[UUID]


class ShopUnitImportSchema(BaseShopUnitSchema):
    price: Optional[int]

    @validator('price')
    @classmethod
    def validate_price(cls, value: Optional[int], values: dict):
        if value is not None and values['type'] == ShopUnitType.CATEGORY:
            raise ValueError

        if value is None and values['type'] == ShopUnitType.OFFER:
            raise ValueError

        return value


class ShopUnitStatisticSchema(BaseShopUnitSchema):
    price: Optional[int]
    date: datetime


class ShopUnitSchema(ShopUnitStatisticSchema):
    children: Optional[List['ShopUnitSchema']]

    @classmethod
    def from_nodes(
        cls, 
        nodes: Iterable['ShopUnitSchema']
    ) -> 'ShopUnitSchema':
        root = next(nodes)
        children: DefaultDict[UUID, List['ShopUnitSchema']] = defaultdict(list)
        for child in nodes:
            children[child.parent_id].append(child)

        parents = deque([root])
        while parents:
            parent = parents.popleft()
            if parent.type == ShopUnitType.OFFER:
                parent.children = None
                continue
            parent.children = children[parent.id]
            parents.extend(parent.children)
        return root


ShopUnitSchema.update_forward_refs()


class ShopUnitsListSchema(BaseSchema):
    items: List[ShopUnitStatisticSchema]


class ShopUnitsListImportSchema(BaseSchema):
    items: List[ShopUnitImportSchema]
    update_date: datetime

    update_date_validator = datetime_iso8601_validator('update_date')
