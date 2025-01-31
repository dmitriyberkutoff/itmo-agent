import os
import requests
from utils.clean import clean_text
from random import choice
from bs4 import BeautifulSoup
from utils.logger import log_info
import xml.etree.ElementTree as ET


user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
]


def random_user_agent():
    agent = choice(user_agent_list)
    return {'User-Agent': agent}


class SearchApi(object):

    def __init__(self, folder_id, api_key, proxies=None):
        self.folder_id = folder_id
        self.api_key = api_key
        self.proxies = proxies

    async def get_results(self, query, num_results=3):
        user_credentials = 'https://yandex.ru/search/xml?folderid={}&apikey={}'.format(self.folder_id, self.api_key)
        query_local_lang = '&query={}'.format(query.replace(' ', '+'))
        results = '&groupby=attr%3D%22%22.mode%3Dflat.groups-on-page%3D{}.docs-in-group%3D1'.format(num_results)
        final_request = '{}{}{}'.format(user_credentials, query_local_lang, results)

        try:
            r = requests.get(final_request, headers=random_user_agent(), proxies=self.proxies)
            result = r.text
        except:
            print('Undocumented Error')
        return result

    async def extract_urls_from_xml(self, xml: str):
        '''Extracting urls from xml which is Yandex Search API result'''
        root = ET.fromstring(xml)
        urls = []

        for doc in root.findall(".//doc"):
            url = doc.find("url").text
            urls.append(url)

            if len(urls) == 3:
                break

        return urls


    def fetch_text_from_url(self, url):
        '''Requests data from the url and returns the basic-cleaned text from the page'''
        try:
            headers = random_user_agent()
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            text = soup.get_text(separator=" ")
            text = " ".join(text.split())

            del soup
            return clean_text(text)[:10000]
        except requests.RequestException as e:
            return f"Error fetching {url}: {e}"

    async def search(self, query):
        '''Searches for information on the Internet on request, returning three popular sites and the text on them'''
        await log_info(f'Starting search for {query}')

        xml = await self.get_results(query)
        soup = str(BeautifulSoup(xml, 'lxml-xml'))

        urls = await self.extract_urls_from_xml(soup)
        texts = {url: self.fetch_text_from_url(url) for url in urls}

        return texts


search_scraper = SearchApi(os.getenv('YANDEX_FOLDER_ID'), os.getenv('YANDEX_SEARCH_API_KEY'))
