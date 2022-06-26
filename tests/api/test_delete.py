from http import HTTPStatus
from httpx import AsyncClient
import pytest

from .utils import make_delete_request, make_imports_request


SHOP_UNITS = [
    {
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'parentId': None
    },
    {
        'type': 'CATEGORY',
        'name': 'Смартфоны',
        'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1'
    },
    {
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 79999
    }
]


@pytest.fixture(autouse=True)
async def import_shop_units(api_client: AsyncClient):
    await make_imports_request(api_client, SHOP_UNITS, '2022-02-04T00:00:00.000Z')


@pytest.mark.asyncio
async def test_cascade_deletions(api_client: AsyncClient):
    root, *_ = SHOP_UNITS
    response = await make_delete_request(api_client, root['id'])
    assert response.status_code == HTTPStatus.OK

    for node in SHOP_UNITS:
        response = await make_delete_request(api_client, node['id'])
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_reversed_deletion(api_client: AsyncClient):
    for shop_unit in reversed(SHOP_UNITS):
        response = await make_delete_request(api_client, shop_unit['id'])
        assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_non_existent_shop_unit(api_client: AsyncClient):
    response = await make_delete_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df2')
    assert response.status_code == HTTPStatus.NOT_FOUND
