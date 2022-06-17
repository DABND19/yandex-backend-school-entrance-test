from datetime import datetime
from typing import Optional

from sqlalchemy import sql

from market.db.models import ShopUnitImport


def select_latest_imports_keys(*conditions) -> sql.Select:
    q = sql.select(
        ShopUnitImport.id,
        sql.func.last_value(ShopUnitImport.date).over(
            partition_by=[ShopUnitImport.id],
            order_by=[ShopUnitImport.date],
            range_=(None, None)
        ).label('date')
    ).distinct()
    if conditions:
        q = q.where(*conditions)
    return q


def select_latest_imports(
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    *conditions
) -> sql.Select:
    conditions = list(conditions)
    if date_start is not None:
        conditions.append(
            ShopUnitImport.date >= date_start
        )
    if date_end is not None:
        conditions.append(
            ShopUnitImport.date <= date_end
        )
    subq = select_latest_imports_keys(*conditions)
    subq = subq.subquery()

    q = sql.select(ShopUnitImport).join_from(
        ShopUnitImport,
        subq,
        sql.and_(
            ShopUnitImport.id == subq.c.id,
            ShopUnitImport.date == subq.c.date
        )
    )
    return q
