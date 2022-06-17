from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List
from uuid import UUID

import asyncpg.exceptions
from fastapi import Depends, HTTPException
from sqlalchemy import orm, sql
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession
from market.db.models.shop_unit import ShopUnitType

from market.schemas import (
    ShopUnitsListImportSchema, ShopUnitSchema,
    ShopUnitsListSchema
)
from market.db import get_session
from market.db.models import ShopUnit, ShopUnitImport
from market.db.queries import select_latest_imports
from market.schemas.shop import ShopUnitImportSchema


class ShopService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    @staticmethod
    def _solve_insertion_order(
        items: List[ShopUnitImportSchema]
    ) -> List[ShopUnitImportSchema]:
        to_order = {
            item.id: item
            for item in items
        }
        if len(to_order) != len(items):
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                'Import items must contain unique ids'
            )
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

    async def import_shop_units(
        self,
        payload: ShopUnitsListImportSchema
    ) -> None:
        if not payload.items:
            return

        async with self.session.begin():
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
            except sqlalchemy.exc.IntegrityError as error:
                if isinstance(
                    error.orig,
                    asyncpg.exceptions.CheckViolationError
                ):
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST,
                        'Only the CATEGORY can be parent of the CATEGORY/OFFER'
                    )
                if isinstance(
                    error.orig,
                    asyncpg.exceptions.ForeignKeyViolationError
                ):
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST, 'Shop units dependencies conflict'
                    )
                raise

            q = postgresql.insert(ShopUnitImport).values([
                {**item.dict(), 'date': payload.update_date}
                for item in payload.items
            ])
            try:
                await self.session.execute(q)
            except sqlalchemy.exc.IntegrityError as error:
                if isinstance(
                    error.orig,
                    asyncpg.exceptions.ForeignKeyViolationError
                ):
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST,
                        'Shop unit\'s type can\'t be changed'
                    )
                raise

    async def delete_shop_unit(self, shop_unit_id: UUID) -> None:
        async with self.session.begin():
            q = sql.delete(ShopUnit).where(
                ShopUnit.id == shop_unit_id
            ).returning(ShopUnit.id)

            records = await self.session.execute(q)
            if not records.scalar():
                raise HTTPException(HTTPStatus.NOT_FOUND, 'Item not found')

    async def get_shop_unit_nodes(self, shop_unit_id: UUID) -> ShopUnitSchema:
        async with self.session.begin():
            latest_imports = select_latest_imports()
            latest_imports = latest_imports.cte()
            latest_import = orm.aliased(ShopUnitImport, latest_imports)

            nodes = sql.select(
                latest_import,
                sql.literal(1).label('level')
            ).where(
                latest_import.id == shop_unit_id
            )
            nodes = nodes.cte(recursive=True)
            tmp = sql.select(
                latest_import,
                (nodes.c.level + 1).label('level')
            ).join_from(
                latest_imports, nodes,
                nodes.c.id == latest_import.parent_id
            )
            nodes = nodes.union_all(tmp)

            node_children = sql.select(
                latest_import.id,
                latest_import.parent_id,
                latest_import.date,
                latest_import.price
            ).where(
                latest_import.type == ShopUnitType.OFFER
            )
            node_children = node_children.cte(recursive=True)
            tmp = sql.select(
                latest_import.id,
                latest_import.parent_id,
                sql.func.greatest(
                    latest_import.date,
                    node_children.c.date
                ),
                node_children.c.price
            ).join_from(
                latest_imports, node_children,
                latest_import.id == node_children.c.parent_id
            )
            node_children = node_children.union_all(tmp)
            actual_prices = sql.select(
                node_children.c.id,
                sql.func.max(
                    node_children.c.date
                ).label('date'),
                sql.func.avg(
                    node_children.c.price
                ).label('price')
            ).group_by(
                node_children.c.id
            )
            actual_prices = actual_prices.subquery()

            subq = sql.select(
                nodes.c.id,
                nodes.c.type,
                sql.func.coalesce(
                    actual_prices.c.date,
                    nodes.c.date
                ).label('date'),
                nodes.c.parent_id,
                nodes.c.name,
                actual_prices.c.price,
                nodes.c.level
            ).join_from(
                nodes, actual_prices,
                nodes.c.id == actual_prices.c.id,
                isouter=True
            ).subquery()
            node = orm.aliased(ShopUnitImport, subq, adapt_on_names=True)
            q = sql.select(node).order_by(
                subq.c.level, subq.c.parent_id, subq.c.id
            )
            result = await self.session.execute(q)
            records = result.scalars().all()
            if not records:
                raise HTTPException(HTTPStatus.NOT_FOUND, 'Item not found')
            return ShopUnitSchema.from_nodes(map(ShopUnitSchema.from_orm, records))

    async def get_sales(self, date_: datetime) -> ShopUnitsListSchema:
        q = select_latest_imports(
            date_ - timedelta(days=1),
            date_,
            ShopUnitImport.type == ShopUnitType.OFFER
        )
        records = await self.session.execute(q)
        return ShopUnitsListSchema(items=records.scalars().all())
