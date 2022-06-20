from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import orm, sql
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from market.db import get_session
from market.db.models import ShopUnit, ShopUnitImport, ShopUnitType
from market.schemas import (
    ShopUnitsListImportSchema, ShopUnitSchema,
    ShopUnitsListSchema, ShopUnitImportSchema
)


class MarketService:
    VALIDATION_ERROR = HTTPException(
        HTTPStatus.BAD_REQUEST, 'Validation Failed'
    )
    NOT_FOUND_ERROR = HTTPException(
        HTTPStatus.NOT_FOUND, 'Item not found'
    )

    def __init__(
        self, 
        session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    @classmethod
    def _solve_insertion_order(
        cls,
        items: List[ShopUnitImportSchema]
    ) -> List[ShopUnitImportSchema]:
        to_order = {
            item.id: item
            for item in items
        }
        if len(to_order) != len(items):
            raise cls.VALIDATION_ERROR
        ordered = []
        for item in items:
            if to_order.pop(item.id, None) is None:
                continue
            dependencies = [item]
            parent_id = item.parent_id
            while parent_id is not None:
                parent = to_order.pop(parent_id, None)
                if parent is None:
                    break
                dependencies.append(parent)
                parent_id = parent.id
            dependencies.reverse()
            ordered.extend(dependencies)
        return ordered

    async def _update_shop_units(
        self, 
        payload: ShopUnitsListImportSchema
    ) -> None:
        q = postgresql.insert(ShopUnit).values([
            {**item.dict(include={'id', 'type', 'parent_id'}),
             'parent_type': ShopUnitType.CATEGORY
             if item.parent_id is not None else None}
            for item in self._solve_insertion_order(payload.items)
        ])
        q = q.on_conflict_do_update(
            index_elements=['id'],
            set_={'parent_id': q.excluded.parent_id,
                  'parent_type': q.excluded.parent_type}
        )
        try:
            await self.session.execute(q)
        except sqlalchemy.exc.IntegrityError:
            raise self.VALIDATION_ERROR

    async def _create_shop_unit_imports(
        self, 
        payload: ShopUnitsListImportSchema
    ) -> None:
        q = postgresql.insert(ShopUnitImport).values([
            {**item.dict(), 'date': payload.update_date}
            for item in payload.items
        ]).returning(ShopUnitImport.id)
        try:
            await self.session.execute(q)
        except sqlalchemy.exc.IntegrityError:
            raise self.VALIDATION_ERROR

        subq = sql.select(ShopUnitImport.id).where(
            ShopUnitImport.date == payload.update_date
        ).scalar_subquery()
        q = sql.update(ShopUnitImport).values(
            expiration_date=payload.update_date
        ).where(
            ShopUnitImport.date < payload.update_date,
            ShopUnitImport.expiration_date.is_(None),
            ShopUnitImport.id == sql.any_(subq)
        ).execution_options(synchronize_session=False)
        await self.session.execute(q)

    async def import_shop_units(
        self,
        payload: ShopUnitsListImportSchema
    ) -> None:
        if not payload.items:
            return

        async with self.session.begin():
            await self._update_shop_units(payload)
            await self._create_shop_unit_imports(payload)

    async def delete_shop_unit(self, shop_unit_id: UUID) -> None:
        async with self.session.begin():
            q = sql.delete(ShopUnit).where(
                ShopUnit.id == shop_unit_id
            ).returning(ShopUnit.id)

            records = await self.session.execute(q)
            if not records.scalar():
                raise self.NOT_FOUND_ERROR

    async def get_shop_unit_nodes(self, shop_unit_id: UUID) -> ShopUnitSchema:
        async with self.session.begin():
            nodes = sql.select(
                ShopUnit,
                sql.literal(1).label('level')
            ).where(
                ShopUnit.id == shop_unit_id
            ).cte(recursive=True)
            tmp = sql.select(
                ShopUnit,
                (nodes.c.level + 1).label('level')
            ).join(
                nodes,
                ShopUnit.parent_id == nodes.c.id
            )
            nodes = nodes.union_all(tmp)

            offers = sql.select(
                ShopUnitImport.id,
                ShopUnitImport.parent_id,
                ShopUnitImport.date,
                ShopUnitImport.price
            ).join(
                nodes,
                ShopUnitImport.id == nodes.c.id
            ).where(
                ShopUnitImport.type == ShopUnitType.OFFER,
                ShopUnitImport.expiration_date.is_(None)
            ).cte(recursive=True)
            tmp = sql.select(
                ShopUnitImport.id,
                ShopUnitImport.parent_id,
                offers.c.date,
                offers.c.price
            ).join(
                offers,
                ShopUnitImport.id == offers.c.parent_id
            ).where(
                ShopUnitImport.expiration_date.is_(None)
            )
            offers = offers.union_all(tmp)
            prices = sql.select(
                offers.c.id.label('shop_unit_id'),
                sql.func.max(offers.c.date).label('date'),
                sql.func.avg(offers.c.price).label('price')
            ).group_by(
                offers.c.id
            ).subquery()

            subq = sql.select(
                ShopUnitImport.id,
                ShopUnitImport.type,
                sql.func.greatest(
                    ShopUnitImport.date, prices.c.date
                ).label('date'),
                ShopUnitImport.parent_id,
                ShopUnitImport.name,
                prices.c.price,
                nodes.c.level
            ).join(
                nodes,
                nodes.c.id == ShopUnitImport.id
            ).join(
                prices,
                ShopUnitImport.id == prices.c.shop_unit_id,
                isouter=True
            ).where(
                ShopUnitImport.expiration_date.is_(None)
            ).subquery()
            node = orm.aliased(ShopUnitImport, subq, adapt_on_names=True)
            q = sql.select(node).order_by(
                subq.c.level, node.parent_id, node.id
            )

            result = await self.session.scalars(q)
            records = result.all()
            if not records:
                raise self.NOT_FOUND_ERROR
            return ShopUnitSchema.from_nodes(map(
                ShopUnitSchema.from_orm, records
            ))

    async def get_sales(self, date_: datetime) -> ShopUnitsListSchema:
        date_start = date_ - timedelta(days=1)
        date_end = date_
        period = sql.func.tsrange(date_start, date_end, '[]')
        q = sql.select(
            ShopUnitImport
        ).where(
            ShopUnitImport.type == ShopUnitType.OFFER,
            period.op('@>')(ShopUnitImport.date),
            ShopUnitImport.actuality_interval.op('@>')(date_end)
        )
        result = await self.session.scalars(q)
        return ShopUnitsListSchema(items=result.all())

    async def get_shop_unit_statistic(
        self, 
        shop_unit_id: UUID,
        date_start: Optional[datetime],
        date_end: Optional[datetime]
    ) -> ShopUnitsListSchema:
        pass
