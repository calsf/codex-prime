import aiohttp
import asyncio


# Create single session
async def create_session():
    return aiohttp.ClientSession()
loop = asyncio.get_event_loop()
session = loop.run_until_complete(create_session())


# Make request and convert json data, return 0 if unable to retrieve data
async def request(data):
    async with session.get(f'https://api.warframestat.us/pc/{data}') as res:
        if res.status is 200:
            return await res.json() #
        else:
            return 0
