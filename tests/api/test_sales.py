from http import HTTPStatus
from typing import Any, Dict, List

from httpx import AsyncClient
import pytest

from .test_nodes import import_nodes
from .utils import (
    make_sales_request, make_imports_request, 
    make_delete_request
)


@pytest.mark.parametrize('date_', [
    '2022-02-04T15:00:00.001Z', '2022-02-01T11:59:59.999Z', '2022-02-01T12:00:00.000Z'
])
@pytest.mark.asyncio
async def test_beyond_interval(api_client: AsyncClient, date_: str):
    response = await make_sales_request(api_client, date_)
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    assert not payload['items']


def _sort_sales(items: List[Dict[str, Any]]) -> None:
    items.sort(key=lambda item: (item['date'], item['id']))


@pytest.mark.asyncio
async def test_basic(api_client: AsyncClient):
    response = await make_sales_request(api_client, '2022-02-03T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_sales(items)

    expected_sales = [
        {
            'type': 'OFFER',
            'name': 'Goldstar 65\' LED UHD LOL Very Smart',
            'id': '73bc3b36-02d1-4245-ab35-3106c9ee1c65',
            'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'price': 69999,
            'date': '2022-02-03T15:00:00.000Z'
        },
        {
            'type': 'OFFER',
            'name': 'Samson 70\' LED UHD Smart',
            'id': '98883e8f-0507-482f-bce2-2fb306cf6483',
            'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'price': 32999,
            'date': '2022-02-03T12:00:00.000Z'
        },
        {
            'type': 'OFFER',
            'name': 'Phyllis 50\' LED UHD Smarter',
            'id': '74b81fda-9cdc-4b63-8927-c978afed5cf4',
            'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'price': 49999,
            'date': '2022-02-03T12:00:00.000Z'
        }
    ]
    _sort_sales(expected_sales)
    assert items == expected_sales


@pytest.mark.asyncio
async def test_shop_unit_update(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 89999
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_sales_request(api_client, '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']

    expected_sales = [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 89999,
        'date': '2022-06-26T15:00:00.000Z'
    }]

    assert items == expected_sales


@pytest.mark.asyncio
async def test_shop_unit_deletion(api_client: AsyncClient):
    response = await make_delete_request(api_client, '74b81fda-9cdc-4b63-8927-c978afed5cf4')
    assert response.status_code == HTTPStatus.OK

    response = await make_sales_request(api_client, '2022-02-03T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_sales(items)

    expected_sales = [
        {
            'type': 'OFFER',
            'name': 'Goldstar 65\' LED UHD LOL Very Smart',
            'id': '73bc3b36-02d1-4245-ab35-3106c9ee1c65',
            'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'price': 69999,
            'date': '2022-02-03T15:00:00.000Z'
        },
        {
            'type': 'OFFER',
            'name': 'Samson 70\' LED UHD Smart',
            'id': '98883e8f-0507-482f-bce2-2fb306cf6483',
            'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'price': 32999,
            'date': '2022-02-03T12:00:00.000Z'
        }
    ]
    _sort_sales(expected_sales)
    assert items == expected_sales


async def test_change_and_delete_previous_parent(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 79999
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_delete_request(api_client, 'd515e43f-f3f6-4471-bb77-6b455017a2d2')
    assert response.status_code == HTTPStatus.OK

    response = await make_sales_request(api_client, '2022-02-02T12:00:00.000Z')    
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']

    expected_sales = [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': 79999,
        'date': '2022-02-02T12:00:00.000Z'
    }]
    assert items == expected_sales

    response = await make_sales_request(api_client, '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']

    expected_sales = [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 79999,
        'date': '2022-06-26T15:00:00.000Z'
    }]
    assert items == expected_sales
