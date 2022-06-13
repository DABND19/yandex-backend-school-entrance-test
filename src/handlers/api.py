from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException,
    Path, Query, Response
)

from src.schemas import (
    ShopUnitsListImportSchema,
    ShopUnitSchema, ShopUnitsListSchema
)
from src.schemas.base import datetime_iso8601_decoder
from src.services import ShopService


router = APIRouter()


@router.post('/imports', response_class=Response)
async def import_shop_units(
    payload: ShopUnitsListImportSchema,
    service: ShopService = Depends()
):
    await service.import_shop_units(payload)
    return Response()


@router.delete('/delete/{id}', response_class=Response)
async def delete_shop_unit(
    id_: UUID = Path(alias='id'),
    service: ShopService = Depends()
):
    await service.delete_shop_unit(id_)
    return Response()


@router.get('/nodes/{id}', response_model=ShopUnitSchema)
async def get_nodes(
    id_: UUID = Path(alias='id'),
    service: ShopService = Depends()
):
    return await service.get_shop_unit_nodes(id_)


def get_strict_date(**kwargs):
    def parser(value: str = Query(**kwargs, format='date')) -> datetime:
        try:
            return datetime_iso8601_decoder(value)
        except ValueError:
            raise HTTPException(HTTPStatus.BAD_REQUEST, 'Invalid date format')
    return parser


@router.get('/sales', response_model=ShopUnitsListSchema)
async def get_sales(
    date_: datetime = Depends(get_strict_date(default=..., alias='date')),
    service: ShopService = Depends()
):
    return await service.get_sales(date_)


@router.get('/node/{id}/statistic', response_model=ShopUnitsListSchema)
async def get_node_statistic(
    date_start: datetime = Depends(get_strict_date(alias='dateStart')),
    date_end: datetime = Depends(get_strict_date(alias='dateEnd')),
    id_: UUID = Path(alias='id'),
    service: ShopService = Depends()
):
    return
