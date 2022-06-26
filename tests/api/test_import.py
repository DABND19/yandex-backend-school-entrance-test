from http import HTTPStatus
from itertools import permutations

from httpx import AsyncClient
import pytest

from .utils import make_imports_request


@pytest.mark.parametrize('items', permutations([
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
]))
@pytest.mark.asyncio
async def test_items_permutations(api_client: AsyncClient, items):
    response = await make_imports_request(api_client, items, '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_non_unique_ids(api_client: AsyncClient):
    response = await make_imports_request(api_client, [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None
        }
    ], '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_parent_id_violation(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 79999
    }], '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_shop_unit_type_change(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': 79999
    }], '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_imports_request(api_client, [{
        'type': 'CATEGORY',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': 79999
    }], '2022-02-05T00:00:00.000Z')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_parent_type_violation(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': 79999
    }], '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'Xomiа Readme 10',
        'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
        'parentId': '863e1a7a-1304-42ae-943b-179184c077e3',
        'price': 59999
    }], '2022-02-05T00:00:00.000Z')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize('items', [
    {
        'type': 'CATEGORY',
        'name': 'Смартфоны',
        'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'parentId': None,
        'price': 70000
    },
    {
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': None
    }
])
@pytest.mark.asyncio
async def test_shop_unit_price_validation(api_client: AsyncClient, items):
    response = await make_imports_request(api_client, items, '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_empty_shop_units_list(api_client: AsyncClient):
    response = await make_imports_request(api_client, [], '2022-02-04T00:00:00.000Z')
    assert response.status_code == HTTPStatus.OK
