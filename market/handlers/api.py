from datetime import datetime
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException,
    Path, Query, Response
)

from market.schemas import (
    ShopUnitsListImportSchema,
    ShopUnitSchema, ShopUnitsListSchema
)
from market.schemas.base import datetime_iso8601_decoder
from market.services import MarketService


router = APIRouter()


@router.post(
    '/imports',
    response_class=Response, 
    tags=['Основные задачи']
)
async def import_shop_units(
    payload: ShopUnitsListImportSchema,
    service: MarketService = Depends()
):
    await service.import_shop_units(payload)
    return Response()


@router.delete(
    '/delete/{id}',
    response_class=Response,
    tags=['Основные задачи']
)
async def delete_shop_unit(
    id_: UUID = Path(alias='id'),
    service: MarketService = Depends()
):
    await service.delete_shop_unit(id_)
    return Response()


@router.get(
    '/nodes/{id}', 
    response_model=ShopUnitSchema,
    tags=['Основные задачи']
)
async def get_nodes(
    id_: UUID = Path(alias='id'),
    service: MarketService = Depends()
):
    return await service.get_shop_unit_nodes(id_)


def get_strict_date(**kwargs):
    if kwargs.get('default') is ...:
        annotation = str
    else:
        annotation = Optional[str]
    def parser(value: annotation = Query(**kwargs, format='date')) -> datetime:
        if value is None:
            return None
        try:
            return datetime_iso8601_decoder(value)
        except ValueError:
            raise HTTPException(HTTPStatus.BAD_REQUEST, 'Validation Failed')
    return parser


@router.get(
    '/sales', 
    response_model=ShopUnitsListSchema,
    tags=['Дополнительные задачи']
)
async def get_sales(
    date_: datetime = Depends(get_strict_date(default=..., alias='date')),
    service: MarketService = Depends()
):
    return await service.get_sales(date_)


@router.get(
    '/node/{id}/statistic',
    response_model=ShopUnitsListSchema,
    tags=['Дополнительные задачи']
)
async def get_node_statistic(
    id_: UUID = Path(alias='id'),
    date_start: datetime = Depends(get_strict_date(default=None, alias='dateStart')),
    date_end: datetime = Depends(get_strict_date(default=None, alias='dateEnd')),
    service: MarketService = Depends()
):
    return await service.get_shop_unit_statistic(
        id_, date_start, date_end
    )
