from http import HTTPStatus
from typing import Any, Dict, List

from httpx import AsyncClient
import pytest

from .utils import (
    make_delete_request, make_imports_request, 
    make_nodes_request
)


@pytest.fixture(autouse=True)
async def import_nodes(api_client: AsyncClient):
    import_batches = [
        {
            'items': [
                {
                    'type': 'CATEGORY',
                    'name': 'Товары',
                    'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                    'parentId': None
                }
            ],
            'updateDate': '2022-02-01T12:00:00.000Z'
        },
        {
            'items': [
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
                },
                {
                    'type': 'OFFER',
                    'name': 'Xomiа Readme 10',
                    'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
                    'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                    'price': 59999
                }
            ],
            'updateDate': '2022-02-02T12:00:00.000Z'
        },
        {
            'items': [
                {
                    'type': 'CATEGORY',
                    'name': 'Телевизоры',
                    'id': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1'
                },
                {
                    'type': 'OFFER',
                    'name': 'Samson 70\' LED UHD Smart',
                    'id': '98883e8f-0507-482f-bce2-2fb306cf6483',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 32999
                },
                {
                    'type': 'OFFER',
                    'name': 'Phyllis 50\' LED UHD Smarter',
                    'id': '74b81fda-9cdc-4b63-8927-c978afed5cf4',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 49999
                }
            ],
            'updateDate': '2022-02-03T12:00:00.000Z'
        },
        {
            'items': [
                {
                    'type': 'OFFER',
                    'name': 'Goldstar 65\' LED UHD LOL Very Smart',
                    'id': '73bc3b36-02d1-4245-ab35-3106c9ee1c65',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 69999
                }
            ],
            'updateDate': '2022-02-03T15:00:00.000Z'
        }
    ]
    for batch in import_batches:
        await make_imports_request(api_client, batch['items'], batch['updateDate'])


def _gen_subtrees(root: Dict[str, Any]) -> List[Dict[str, Any]]:
    subtrees = [root]
    for tree in subtrees:
        children = tree.get('children')
        if children is None:
            continue
        subtrees.extend(children)
    return subtrees


def _deep_sort_children(node: Dict[str, Any]) -> None:
    if node.get('children'):
        node['children'].sort(key=lambda x: x['id'])

        for child in node['children']:
            _deep_sort_children(child)


@pytest.mark.parametrize('tree', _gen_subtrees({
    'type': 'CATEGORY',
    'name': 'Товары',
    'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
    'price': 58599,
    'parentId': None,
    'date': '2022-02-03T15:00:00.000Z',
    'children': [
        {
            'type': 'CATEGORY',
            'name': 'Телевизоры',
            'id': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
            'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 50999,
            'date': '2022-02-03T15:00:00.000Z',
            'children': [
                {
                    'type': 'OFFER',
                    'name': 'Samson 70\' LED UHD Smart',
                    'id': '98883e8f-0507-482f-bce2-2fb306cf6483',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 32999,
                    'date': '2022-02-03T12:00:00.000Z',
                    'children': None,
                },
                {
                    'type': 'OFFER',
                    'name': 'Phyllis 50\' LED UHD Smarter',
                    'id': '74b81fda-9cdc-4b63-8927-c978afed5cf4',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 49999,
                    'date': '2022-02-03T12:00:00.000Z',
                    'children': None
                },
                {
                    'type': 'OFFER',
                    'name': 'Goldstar 65\' LED UHD LOL Very Smart',
                    'id': '73bc3b36-02d1-4245-ab35-3106c9ee1c65',
                    'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                    'price': 69999,
                    'date': '2022-02-03T15:00:00.000Z',
                    'children': None
                }
            ]
        },
        {
            'type': 'CATEGORY',
            'name': 'Смартфоны',
            'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
            'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
            'price': 69999,
            'date': '2022-02-02T12:00:00.000Z',
            'children': [
                {
                    'type': 'OFFER',
                    'name': 'jPhone 13',
                    'id': '863e1a7a-1304-42ae-943b-179184c077e3',
                    'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                    'price': 79999,
                    'date': '2022-02-02T12:00:00.000Z',
                    'children': None
                },
                {
                    'type': 'OFFER',
                    'name': 'Xomiа Readme 10',
                    'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
                    'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                    'price': 59999,
                    'date': '2022-02-02T12:00:00.000Z',
                    'children': None
                }
            ]
        },
    ]
}))
@pytest.mark.asyncio
async def test_nodes_basic(api_client: AsyncClient, tree):
    response = await make_nodes_request(api_client, tree['id'])
    assert response.status_code == HTTPStatus.OK

    payload = response.json()

    _deep_sort_children(payload)
    _deep_sort_children(tree)
    assert payload == tree


@pytest.mark.asyncio
async def test_child_deletion(api_client: AsyncClient):
    response = await make_delete_request(api_client, '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2')
    assert response.status_code == HTTPStatus.OK

    response = await make_nodes_request(api_client, '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2')
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = await make_nodes_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    expected_tree = {
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 69999,
        'parentId': None,
        'date': '2022-02-02T12:00:00.000Z',
        'children': [
            {
                'type': 'CATEGORY',
                'name': 'Смартфоны',
                'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                'price': 69999,
                'date': '2022-02-02T12:00:00.000Z',
                'children': [
                    {
                        'type': 'OFFER',
                        'name': 'jPhone 13',
                        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 79999,
                        'date': '2022-02-02T12:00:00.000Z',
                        'children': None
                    },
                    {
                        'type': 'OFFER',
                        'name': 'Xomiа Readme 10',
                        'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 59999,
                        'date': '2022-02-02T12:00:00.000Z',
                        'children': None
                    }
                ]
            },
        ]
    }
    _deep_sort_children(expected_tree)

    payload = response.json()
    _deep_sort_children(payload)

    assert expected_tree == payload


{
    'items': [{
        'type': 'CATEGORY',
        'name': 'Телевизоры',
        'id': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
        'parentId': None
    }], 
    'updateDate': '2022-06-26T15:00:00.000Z'
}


@pytest.mark.asyncio
async def test_change_parent(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'CATEGORY',
        'name': 'Телевизоры',
        'id': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
        'parentId': None
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_nodes_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    expected_tree = {
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 69999,
        'parentId': None,
        'date': '2022-06-26T15:00:00.000Z',
        'children': [
            {
                'type': 'CATEGORY',
                'name': 'Смартфоны',
                'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                'price': 69999,
                'date': '2022-02-02T12:00:00.000Z',
                'children': [
                    {
                        'type': 'OFFER',
                        'name': 'jPhone 13',
                        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 79999,
                        'date': '2022-02-02T12:00:00.000Z',
                        'children': None
                    },
                    {
                        'type': 'OFFER',
                        'name': 'Xomiа Readme 10',
                        'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 59999,
                        'date': '2022-02-02T12:00:00.000Z',
                        'children': None
                    }
                ]
            },
        ]
    }
    _deep_sort_children(expected_tree)

    payload = response.json()
    _deep_sort_children(payload)

    assert expected_tree == payload


async def test_children_update(api_client: AsyncClient):
    response = await make_imports_request(api_client, [{
        'type': 'OFFER',
        'name': 'jPhone 13',
        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
        'price': 89999
    }], '2022-06-26T15:00:00.000Z')
    assert response.status_code == HTTPStatus.OK

    response = await make_nodes_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    payload = response.json()
    _deep_sort_children(payload)

    expected_tree = {
        'type': 'CATEGORY',
        'name': 'Товары',
        'id': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        'price': 60599,
        'parentId': None,
        'date': '2022-06-26T15:00:00.000Z',
        'children': [
            {
                'type': 'CATEGORY',
                'name': 'Телевизоры',
                'id': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                'price': 50999,
                'date': '2022-02-03T15:00:00.000Z',
                'children': [
                    {
                        'type': 'OFFER',
                        'name': 'Samson 70\' LED UHD Smart',
                        'id': '98883e8f-0507-482f-bce2-2fb306cf6483',
                        'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                        'price': 32999,
                        'date': '2022-02-03T12:00:00.000Z',
                        'children': None,
                    },
                    {
                        'type': 'OFFER',
                        'name': 'Phyllis 50\' LED UHD Smarter',
                        'id': '74b81fda-9cdc-4b63-8927-c978afed5cf4',
                        'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                        'price': 49999,
                        'date': '2022-02-03T12:00:00.000Z',
                        'children': None
                    },
                    {
                        'type': 'OFFER',
                        'name': 'Goldstar 65\' LED UHD LOL Very Smart',
                        'id': '73bc3b36-02d1-4245-ab35-3106c9ee1c65',
                        'parentId': '1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2',
                        'price': 69999,
                        'date': '2022-02-03T15:00:00.000Z',
                        'children': None
                    }
                ]
            },
            {
                'type': 'CATEGORY',
                'name': 'Смартфоны',
                'id': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                'parentId': '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
                'price': 74999,
                'date': '2022-06-26T15:00:00.000Z',
                'children': [
                    {
                        'type': 'OFFER',
                        'name': 'jPhone 13',
                        'id': '863e1a7a-1304-42ae-943b-179184c077e3',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 89999,
                        'date': '2022-06-26T15:00:00.000Z',
                        'children': None
                    },
                    {
                        'type': 'OFFER',
                        'name': 'Xomiа Readme 10',
                        'id': 'b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4',
                        'parentId': 'd515e43f-f3f6-4471-bb77-6b455017a2d2',
                        'price': 59999,
                        'date': '2022-02-02T12:00:00.000Z',
                        'children': None
                    }
                ]
            },
        ]
    }
    _deep_sort_children(expected_tree)

    assert payload == expected_tree


@pytest.mark.asyncio
async def test_not_found_error(api_client: AsyncClient):
    response = await make_delete_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.OK

    response = await make_nodes_request(api_client, '069cb8d7-bbdd-47d3-ad8f-82ef4c269df1')
    assert response.status_code == HTTPStatus.NOT_FOUND
