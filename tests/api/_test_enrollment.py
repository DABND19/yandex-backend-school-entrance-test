from httpx import AsyncClient
import pytest


ROOT_ID = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

IMPORT_BATCHES = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Товары",
                "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "parentId": None
            }
        ],
        "updateDate": "2022-02-01T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            },
            {
                "type": "OFFER",
                "name": "Samson 70\" LED UHD Smart",
                "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 32999
            },
            {
                "type": "OFFER",
                "name": "Phyllis 50\" LED UHD Smarter",
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 49999
            }
        ],
        "updateDate": "2022-02-03T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Goldstar 65\" LED UHD LOL Very Smart",
                "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 69999
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
]

EXPECTED_TREE = {
    "type": "CATEGORY",
    "name": "Товары",
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
    "price": 58599,
    "parentId": None,
    "date": "2022-02-03T15:00:00.000Z",
    "children": [
        {
            "type": "CATEGORY",
            "name": "Телевизоры",
            "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 50999,
            "date": "2022-02-03T15:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "Samson 70\" LED UHD Smart",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 49999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Goldstar 65\" LED UHD LOL Very Smart",
                    "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 69999,
                    "date": "2022-02-03T15:00:00.000Z",
                    "children": None
                }
            ]
        },
        {
            "type": "CATEGORY",
            "name": "Смартфоны",
            "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 69999,
            "date": "2022-02-02T12:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "jPhone 13",
                    "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 79999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Xomiа Readme 10",
                    "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 59999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None
                }
            ]
        },
    ]
}


class TestEnrollement:
    @classmethod
    def deep_sort_children(cls, node):
        if node.get("children"):
            node["children"].sort(key=lambda x: x["id"])

            for child in node["children"]:
                cls.deep_sort_children(child)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('batch', IMPORT_BATCHES)
    async def test_import(self, batch, api_client: AsyncClient):
        response = await api_client.post("/imports", json=batch)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_nodes(self, api_client: AsyncClient):
        response = await api_client.get(f"/nodes/{ROOT_ID}")
        assert response.status_code == 200

        payload = response.json()
        self.deep_sort_children(payload)
        self.deep_sort_children(EXPECTED_TREE)
        assert payload == EXPECTED_TREE

    @pytest.mark.asyncio
    async def test_sales(self, api_client: AsyncClient):
        response = await api_client.get(f"/sales", params={
            'date': '2022-02-04T00:00:00.000Z'
        })
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_stats(self, api_client: AsyncClient):
        response = await api_client.get(f"/node/{ROOT_ID}/statistic", params={
            "dateStart": "2022-02-01T00:00:00.000Z",
            "dateEnd": "2022-02-03T00:00:00.000Z"
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete(self, api_client: AsyncClient):
        response = await api_client.delete(f"/delete/{ROOT_ID}")
        assert response.status_code == 200

        response = await api_client.get(f"/nodes/{ROOT_ID}")
        assert response.status_code == 404
