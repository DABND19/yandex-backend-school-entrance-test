from http import HTTPStatus
from typing import Any, Dict, List

from httpx import AsyncClient
import pytest

from .test_nodes import import_nodes
from .utils import (
    make_node_statistic_request, make_delete_request,
    make_imports_request
)


def _sort_statistic(items: List[Dict[str, Any]]) -> None:
    items.sort(key=lambda item: item['date'])


@pytest.mark.asyncio
async def test_basic(api_client: AsyncClient):
    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_statistic(items)

    expected_statistic = [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': None,
            'date': '2022-02-01T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 55749,
            'date': '2022-02-03T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 58599,
            'parentId': None,
            'date': '2022-02-03T15:00:00.000Z'
        }
    ]
    _sort_statistic(expected_statistic)

    assert items == expected_statistic


@pytest.mark.asyncio
async def test_delete_children(api_client: AsyncClient):
    response = await make_delete_request(api_client, '73bc3b36-02d1-4245-ab35-3106c9ee1c65')
    assert response.status_code == HTTPStatus.OK

    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_statistic(items)

    expected_statistic = [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': None,
            'date': '2022-02-01T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 55749,
            'date': '2022-02-03T12:00:00.000Z'
        }
    ]
    _sort_statistic(expected_statistic)

    assert items == expected_statistic


@pytest.mark.asyncio
async def test_update_children(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 89999
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_statistic(items)

    expected_statistic = [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': None,
            'date': '2022-02-01T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 55749,
            'date': '2022-02-03T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 58599,
            'parentId': None,
            'date': '2022-02-03T15:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 60599,
            'parentId': None,
            'date': '2022-06-26T15:00:00.000Z'
        }
    ]
    _sort_statistic(expected_statistic)

    assert items == expected_statistic


@pytest.mark.asyncio
async def test_change_parent(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': None,
        'price': 89999
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_statistic(items)

    expected_statistic = [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': None,
            'date': '2022-02-01T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 55749,
            'date': '2022-02-03T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 58599,
            'parentId': None,
            'date': '2022-02-03T15:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 53249,
            'parentId': None,
            'date': '2022-06-26T15:00:00.000Z'
        }
    ]
    _sort_statistic(expected_statistic)

    assert items == expected_statistic


@pytest.mark.parametrize('import_batch', [
    [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 79999
    }],
    [{
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': None,
        'parentId': None
    }]
])
@pytest.mark.asyncio
async def test_state_duplicates(api_client: AsyncClient, import_batch):
    response = await make_imports_request(api_client, import_batch, '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']
    _sort_statistic(items)

    expected_statistic = [
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': None,
            'date': '2022-02-01T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'parentId': None,
            'price': 55749,
            'date': '2022-02-03T12:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 58599,
            'parentId': None,
            'date': '2022-02-03T15:00:00.000Z'
        },
        {
            'type': 'CATEGORY',
            'name': 'Товары',
            'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 58599,
            'parentId': None,
            'date': '2022-06-26T15:00:00.000Z'
        }
    ]
    _sort_statistic(expected_statistic)

    assert items == expected_statistic


@pytest.mark.parametrize('date_start,date_end', [
    (None, '2022-02-01T12:00:00.000Z'), ('2022-02-03T15:00:00.001Z', None)
])
@pytest.mark.asyncio
async def test_beyond_interval(api_client: AsyncClient, date_start, date_end):
    response = await make_node_statistic_request(
        api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1', date_start, date_end
    )
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    assert not payload['items']


@pytest.mark.asyncio
async def test_interval(api_client: AsyncClient):
    response = await make_node_statistic_request(
        api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        '2022-02-01T12:00:00.000Z', '2022-02-02T12:00:00.000Z'
    )
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    items = payload['items']

    expected_statistic = [{
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'parentId': None,
        'price': None,
        'date': '2022-02-01T12:00:00.000Z'
    }]
    assert items == expected_statistic


@pytest.mark.asyncio
async def test_not_found_error(api_client: AsyncClient):
    response = await make_delete_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    response = await make_node_statistic_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.NOT_FOUND
