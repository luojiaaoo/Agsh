import json
from agno.utils.log import log_debug
import httpx
from config import qingtian_settings


async def web_scrape(url: str):
    """
    scrape web content from a given URL.

    Args:
        url (str): The URL of the web page to scrape.

    Returns:
        data with the scraped content.
    """
    user_id: str = '321'
    API_KEY = qingtian_settings.qingtian_web_scrape_api_key
    URL = qingtian_settings.qingtian_url
    payload = {
        'UserID': user_id,
        'InputData': json.dumps(
            {'url': url},
            ensure_ascii=False,
        ),
    }
    headers = {'Apikey': API_KEY, 'Content-Type': 'application/json'}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def volcano_search(query: str):
    """higher priority then bing_search, Use this function to search for a query by volcano.

    Args:
        query(str): The query to search for.

    Returns:
        The result.
    """
    URL = qingtian_settings.qingtian_url
    USER = '321'
    log_debug(f'Searching for: {query} using backend: volcano')
    API_KEY = qingtian_settings.qingtian_volcano_search_api_key
    payload = {
        'UserID': USER,
        'InputData': json.dumps(
            {'query': query},
            ensure_ascii=False,
        ),
    }
    headers = {'Apikey': API_KEY, 'Content-Type': 'application/json'}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(URL, json=payload, headers=headers)
        resp.raise_for_status()
        if resp.json()['status'] == 'success':
            return json.dumps(
                json.loads(resp.json()['output'])['output'],
                indent=2,
                ensure_ascii=False,
            )
        else:
            return f'Volcano search failed with message: {
                json.dumps(
                    resp.json(),
                    indent=2,
                    ensure_ascii=False,
                )
            }'


async def bing_search(query: str):
    """Use this function to search for a query.
    The detailed content can only be obtained by web_scrape.

    Args:
        query(str): The query to search for.

    Returns:
        The briefness result with URL.
    """
    URL = qingtian_settings.qingtian_url
    USER = '321'
    log_debug(f'Searching for: {query} using backend: bing')
    API_KEY = qingtian_settings.qingtian_bing_search_api_key
    payload = {
        'UserID': USER,
        'InputData': json.dumps(
            {'query': query},
            ensure_ascii=False,
        ),
    }
    headers = {'Apikey': API_KEY, 'Content-Type': 'application/json'}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(URL, json=payload, headers=headers)
        resp.raise_for_status()
        return json.dumps(
            resp.json()['output'],
            indent=2,
            ensure_ascii=False,
        )
