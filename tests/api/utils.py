from typing import Any, Dict, List, Optional

from httpx import AsyncClient, Response


async def make_imports_request(
    api_client: AsyncClient,
    items: List[Dict[str, Any]],
    update_date: str
) -> Response:
    return await api_client.post('/imports', json={
        'items': items,
        'updateDate': update_date
    })


async def make_delete_request(api_client: AsyncClient, shop_unit_id: str) -> Response:
    return await api_client.delete(f'/delete/{shop_unit_id}')


async def make_nodes_request(api_client: AsyncClient, shop_unit_id: str) -> Response:
    return await api_client.get(f'/nodes/{shop_unit_id}')


async def make_sales_request(api_client: AsyncClient, date_: str) -> Response:
    return await api_client.get('/sales', params={'date': date_})


async def make_node_statistic_request(
    api_client: AsyncClient,
    shop_unit_id: str,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None
) -> Response:
    params = {}
    if date_start is not None:
        params['dateStart'] = date_start
    if date_end is not None:
        params['dateEnd'] = date_end
    return await api_client.get(f'/node/{shop_unit_id}/statistic', params=params)
