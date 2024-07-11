from tabulate import tabulate
from pyshorteners import Shortener as shortener
import requests
import asyncio, aiohttp

shorter = shortener().tinyurl

class CountryParser:
    def __init__(self, url="https://restcountries.com/v3.1/all?fields=name"):
        self.url = url

        self.names = []
        self.countries = []
        self.flags = []

        self.data = []

    async def fetch_data(self, session):
        async with session.get(self.url) as response:
            return await response.json()

    async def process_names(self):
        async with aiohttp.ClientSession() as session:
            response = await self.fetch_data(session)
            for item in response:
                self.names.append(item['name']['official'])
            return self.names

    async def fetch_country_data(self, session, country):
        async with session.get(f'https://restcountries.com/v3.1/name/{country}') as response:
            return await response.json()

    async def process_countries(self):
        async with aiohttp.ClientSession() as session:
            names = await self.process_names()
            tasks = [self.fetch_country_data(session, country) for country in names]
            results = await asyncio.gather(*tasks)

            for country_response in results:
                if len(country_response) != 1:
                    capital = country_response[1].get('capital', None)
                    self.flags.append(shorter.short(country_response[1]['flags']['png']))
                else:
                    capital = country_response[0].get('capital', None)
                    self.flags.append(shorter.short(country_response[0]['flags']['png']))
                
                self.countries.append(capital)
            return [self.countries, self.flags]

    def parse(self):
        self.countries, self.flags = asyncio.run(self.process_countries())
        self.data = zip(self.names, self.countries, self.flags)
        return tabulate(self.data, headers=['Name', 'Captital', 'Flag_link'])
            

if __name__ == "__main__":
    parser = CountryParser().parse()
    print(parser)
    