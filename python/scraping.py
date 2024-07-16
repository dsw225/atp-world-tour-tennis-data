from bs4 import BeautifulSoup
import aiohttp
import aiofiles
import asyncio
import re
import csv


headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

async def read_proxies(file_path):
    try:
        async with aiofiles.open(file_path, 'r') as csvfile:
            proxies = [line.strip() for line in await csvfile.readlines()]
        proxy_parts = proxies[0].split(':')
        if len(proxy_parts) == 4:
            proxy_host, proxy_port, proxy_user, proxy_pass = proxy_parts
            proxy_url = f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
            auth = aiohttp.BasicAuth(proxy_user, proxy_pass)
        else:  # Proxy without authentication
            proxy_host, proxy_port = proxy_parts
            proxy_url = f'http://{proxy_host}:{proxy_port}'
            auth = None
        return proxy_url, auth
    except FileNotFoundError:
        print(f"Proxy file not found: {file_path}")
        return None, None
    
async def fetch(session, url, proxy_url=None, auth=None):
    retries = 3  # Number of retries
    backoff_factor = 2  # Exponential backoff factor
    while retries > 0:
        try:
            if proxy_url:
                print(f"Fetching URL: {url} with proxy: {proxy_url.split('@')[1]}")
            async with session.get(url, proxy=proxy_url, proxy_auth=auth, headers=headers) as response:
                if response.status == 200:
                    data = await response.text()
                    return data
                elif response.status == 404:
                    print("404 error: No statistics available for this match.")
                    return None
                else:
                    print(f"Request failed with status: {response.status}. Retrying...")
        except aiohttp.ClientError as e:
            print(f"Client error: {e}. Retrying...")
        
        retries -= 1
        await asyncio.sleep(backoff_factor * (3 - retries))  # Exponential backoff
    
    return None
