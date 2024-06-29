from playwright.async_api import async_playwright
import random
from bs4 import BeautifulSoup as bs
import re
import asyncio

async def quick_test():
 async with async_playwright() as p:
   browser = await p.chromium.launch(headless=True)
   page = await browser.new_page()
   await page.goto('https://www.tryhackme.com')
   await page.wait_for_timeout(2000)
   content = await page.content()
   print(content)
   await browser.close()

"""
Use this website https://httpbin.org/headers to check random header
This class was written based on this stackoverflow answer
https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class
"""

"""
Async Playwright is not thread safe so yeah cannot multi thread it with async
"""

class WebScraperCoreAsync():
    async def __aenter__(self, browser='firefox'):
        self.destructor = True
        if browser not in ['firefox', 'edge', 'chrome']:
            print(f'Browser {browser} is not supported')
            self.destructor = False
            return None
        self.pw = await async_playwright().start()
        match browser:
            case 'firefox':
                self.browser = await self.pw.firefox.launch(headless=True)
            case 'edge':
                self.browser = await self.pw.chromium.launch(headless=True)
            case 'chrome':
                self.browser = await self.pw.chromium.launch(headless=True)
            case _:
                self.browser = await self.pw.firefox.launch(headless=True)
        self.bs_allowed_tags = [
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'p',
            'span'
        ]
        self.code_tags = [
            'code',
            'pre'
        ]
        self.user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (X11; Linux aarch64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
        ]
        return self

    def generate_header(self):
        random_user_agent = random.choice(self.user_agents)
        custom_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "en-US,en;q=0.5", 
            "Sec-Fetch-Dest": "document", 
            "Sec-Fetch-Mode": "navigate", 
            "Sec-Fetch-Site": "none", 
            "Sec-Fetch-User": "?1", 
            "Upgrade-Insecure-Requests": "1", 
            "User-Agent": random_user_agent, 
        }
        return custom_header
         
    async def get_website_html(self, url):
        custom_header = self.generate_header()
        page = await self.browser.new_page(extra_http_headers=custom_header)
        response = await page.goto(url)
        # await page.wait_for_timeout(2000)
        # web_html_content = await page.content()
        # await page.close()
        # return web_html_content
        if response.status == 200:
            await page.wait_for_timeout(2000)
            web_html_content = await page.content()
            await page.close()
            return web_html_content
        else:
            web_html_content = await page.content()
            error_message = f'Error code {response.status}, {response.text()}, {web_html_content}'
            await page.close()
            return error_message
    
    async def get_website_content(self, url):
        html_content = await self.get_website_html(url)
        html_parser = bs(html_content, 'html.parser')
        # Extract information in selected tags
        webcontent_text_list = [t.strip().replace('\t', '').replace('\r\n', '') for t in html_parser.find_all(string=True) if t.parent.name in self.bs_allowed_tags and t.strip() != '']
        # Remove non readable data in web content
        webcontent_text_list = [ text for text in webcontent_text_list if not re.match(r'^[^0-9a-zA-Z]+$', text) ]
        # Extract code snippet in the web
        webcontent_code_list = [t.strip().replace('\t', '').replace('\r\n', '') for t in html_parser.find_all(string=True) if t.parent.name in self.code_tags and t.strip() != '']
        webcontent_text = ' '.join(webcontent_text_list)
        webcontent_code = '\n'.join(webcontent_code_list)
        web_content = f'{webcontent_text}\n{webcontent_code}'
        return (url, web_content)

    async def __aexit__(self, *args, **kwargs):
        if self.destructor:
            await self.browser.close()
            await self.pw.stop()

class WebScraperAsync():
    def __init__(self):
        self.core = WebScraperCoreAsync()
        self.loop = asyncio.get_event_loop()

    def get_website_content(self, query):
        return self.loop.run_until_complete(self.async_get_website_content(query))
    
    async def async_get_website_content(self, query):
        async with self.core as web_scraper:
            return await web_scraper.get_website_content(query)
