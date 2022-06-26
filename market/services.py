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
            await self.session.connection(execution_options={
                'isolation_level': 'SERIALIZABLE'
            })
            await self._update_shop_units(payload)
            await self._create_shop_unit_imports(payload)

    async def _check_is_shop_unit_exists(self, shop_unit_id: UUID) -> None:
        subq = sql.exists(ShopUnit.id).where(ShopUnit.id == shop_unit_id)
        q = sql.select(subq)
        if not await self.session.scalar(q):
            raise self.NOT_FOUND_ERROR

    async def delete_shop_unit(self, shop_unit_id: UUID) -> None:
        async with self.session.begin():
            await self._check_is_shop_unit_exists(shop_unit_id)

            q = sql.delete(ShopUnit).where(
                ShopUnit.id == shop_unit_id
            )
            await self.session.execute(q)

    async def get_shop_unit_nodes(self, shop_unit_id: UUID) -> ShopUnitSchema:
        async with self.session.begin():
            await self._check_is_shop_unit_exists(shop_unit_id)

            nodes_history = sql.select(
                ShopUnitImport,
                sql.literal(1).label('level')
            ).where(
                ShopUnitImport.id == shop_unit_id,
                ShopUnitImport.expiration_date.is_(None)
            ).cte(recursive=True)
            parent = orm.aliased(ShopUnitImport, nodes_history)
            tmp = sql.select(
                ShopUnitImport,
                (nodes_history.c.level + 1).label('level')
            ).join(
                nodes_history,
                sql.and_(
                    ShopUnitImport.parent_id == parent.id,
                    parent.actuality_period
                    .op('&&')(ShopUnitImport.actuality_period)
                )
            )
            nodes_history = nodes_history.union_all(tmp)
            node_import = orm.aliased(ShopUnitImport, nodes_history)

            expiration_dates = sql.select(
                node_import.id,
                node_import.parent_id,
                node_import.expiration_date
            ).where(
                node_import.expiration_date.is_not(None)
            ).cte(recursive=True)
            tmp = sql.select(
                node_import.id,
                node_import.parent_id,
                sql.func.greatest(
                    node_import.expiration_date,
                    expiration_dates.c.expiration_date
                ).label('expiration_date')
            ).join(
                expiration_dates,
                sql.and_(
                    expiration_dates.c.parent_id == node_import.id,
                    node_import.actuality_period.op('@>')(expiration_dates.c.expiration_date)
                )
            )
            expiration_dates = expiration_dates.union_all(tmp)

            expiration_dates = sql.select(
                expiration_dates.c.id,
                sql.func.max(
                    expiration_dates.c.expiration_date
                ).label('expiration_date')
            ).group_by(
                expiration_dates.c.id
            ).subquery()

            prices = sql.select(
                node_import.id,
                node_import.parent_id,
                node_import.date,
                node_import.price
            ).where(
                node_import.type == ShopUnitType.OFFER,
                node_import.expiration_date.is_(None)
            ).cte(recursive=True)
            tmp = sql.select(
                node_import.id,
                node_import.parent_id,
                prices.c.date,
                prices.c.price
            ).join(
                prices,
                node_import.id == prices.c.parent_id
            ).where(
                node_import.expiration_date.is_(None)
            )
            prices = prices.union_all(tmp)
            prices = sql.select(
                prices.c.id.label('shop_unit_id'),
                sql.func.max(prices.c.date).label('date'),
                sql.func.avg(prices.c.price).label('price')
            ).group_by(
                prices.c.id
            ).subquery()

            subq = sql.select(
                node_import.id,
                node_import.type,
                sql.func.greatest(
                    node_import.date, prices.c.date, 
                    expiration_dates.c.expiration_date
                ).label('date'),
                node_import.parent_id,
                node_import.name,
                prices.c.price,
                nodes_history.c.level
            ).join(
                prices,
                node_import.id == prices.c.shop_unit_id,
                isouter=True
            ).join(
                expiration_dates,
                node_import.id == expiration_dates.c.id,
                isouter=True
            ).where(
                node_import.expiration_date.is_(None)
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
        async with self.session.begin():
            await self.session.connection(execution_options={
                'isolation_level': 'REPEATABLE READ'
            })
            date_start = date_ - timedelta(days=1)
            date_end = date_
            period = sql.func.tsrange(date_start, date_end, '[]')
            q = sql.select(
                ShopUnitImport
            ).where(
                ShopUnitImport.type == ShopUnitType.OFFER,
                period.op('@>')(ShopUnitImport.date),
                ShopUnitImport.actuality_period.op('@>')(date_end)
            )
            result = await self.session.scalars(q)
            return ShopUnitsListSchema(items=result.all())

    async def get_shop_unit_statistic(
        self,
        shop_unit_id: UUID,
        date_start: Optional[datetime],
        date_end: Optional[datetime]
    ) -> ShopUnitsListSchema:
        async with self.session.begin():
            await self.session.connection(execution_options={
                'isolation_level': 'REPEATABLE READ'
            })
            await self._check_is_shop_unit_exists(shop_unit_id)

            period = sql.func.tsrange(date_start, date_end, '[)')

            # Получим все узлы и их детей,
            # которые менялись в течение заднного периода
            nodes_history = sql.select(
                ShopUnitImport,
                ShopUnitImport.actuality_period
                .op('*')(period).label('actuality_period')
            ).where(
                ShopUnitImport.actuality_period.op('&&')(period),
                ShopUnitImport.id == shop_unit_id
            ).cte(recursive=True)
            tmp = sql.select(
                ShopUnitImport,
                ShopUnitImport.actuality_period
                .op('*')(nodes_history.c.actuality_period)
            ).join(
                nodes_history,
                sql.and_(
                    nodes_history.c.id == ShopUnitImport.parent_id,
                    ShopUnitImport.actuality_period
                    .op('&&')(nodes_history.c.actuality_period)
                )
            )
            nodes_history = nodes_history.union_all(tmp)

            # Цена меняется тогда, когда меняются дочерние узлы
            adding_children_dates = sql.select(
                nodes_history.c.date.label('date')
            ).distinct()
            # Очень важно учесть случай, когда узел перестает быть дочерним
            # это можно отследить по дате истечения актуальности импорта
            removing_children_dates = sql.select(
                nodes_history.c.expiration_date.label('date')
            ).distinct()
            tmp = adding_children_dates.union(
                removing_children_dates).subquery()
            price_change = sql.select(
                sql.func.row_number().over(
                    order_by=[tmp.c.date],
                    range_=(None, None)
                ).label('row_num'),
                tmp.c.date.label('date')
            ).cte()
            next_price_change = sql.alias(price_change)
            # Получим интервалы, в которые потенциально могла измениться цена
            price_change_periods = sql.select(
                sql.func.tsrange(
                    price_change.c.date, next_price_change.c.date, '[)'
                ).label('period')
            ).join_from(
                price_change,
                next_price_change,
                price_change.c.row_num + 1 == next_price_change.c.row_num
            ).subquery()

            # Сопоставим периоды изменения цены и детей
            # для того, чтобы в дальнейшем саггрегировать
            # цену за каждый из периодов
            offers = sql.select(
                nodes_history.c.id,
                nodes_history.c.price,
                price_change_periods.c.period
            ).join_from(
                price_change_periods,
                nodes_history,
                price_change_periods.c.period
                .op('&&')(nodes_history.c.actuality_period)
            ).where(
                nodes_history.c.type == ShopUnitType.OFFER
            ).subquery()

            price_periods = sql.select(
                offers.c.period,
                sql.func.avg(offers.c.price).label('price')
            ).group_by(offers.c.period).subquery()

            # Изменения состоят из изменений цены
            price_changes = sql.select(
                nodes_history.c.id,
                nodes_history.c.type,
                nodes_history.c.parent_id,
                nodes_history.c.name,
                sql.func.lower(price_periods.c.period).label('date'),
                price_periods.c.price
            ).join_from(
                price_periods,
                nodes_history,
                nodes_history.c.actuality_period
                .op('@>')(sql.func.lower(price_periods.c.period))
            ).where(
                nodes_history.c.id == shop_unit_id,
                period.op('@>')(sql.func.lower(price_periods.c.period))
            )

            # А также из изменения полей самого узла
            nodes_changes = sql.select(
                nodes_history.c.id,
                nodes_history.c.type,
                nodes_history.c.parent_id,
                nodes_history.c.name,
                nodes_history.c.date,
                price_periods.c.price
            ).join_from(
                nodes_history,
                price_periods,
                price_periods.c.period
                .op('@>')(nodes_history.c.date),
                isouter=True
            ).where(
                nodes_history.c.id == shop_unit_id,
                period.op('@>')(nodes_history.c.date)
            )

            changes = price_changes.union(nodes_changes).subquery()
            node = orm.aliased(ShopUnitImport, changes, adapt_on_names=True)

            # Выбираем уникальные изменения, ведь дата изменения цены
            # могла совпасть с датой изменения узла
            q = sql.select(node).order_by(
                node.date
            )
            result = await self.session.scalars(q)
            return ShopUnitsListSchema(items=result.all())
