from playwright.sync_api import sync_playwright
import random
from bs4 import BeautifulSoup as bs
import re

"""
Use this website https://httpbin.org/headers to check random header
"""

"""
Have to create new sunc Playwright instance to run multi thread
Open and close many browsers
Thinking about Selenium, it is the same for each web
Selenium does not support open multi web in one Selenium browser
"""
class WebScraperSyncOneBrowser():
    def __init__(self, browser='firefox'):
        self.destructor = True
        if browser not in ['firefox', 'edge', 'chrome']:
            print(f'Browser {browser} is not supported')
            self.destructor = False
            return None
        self.pw = sync_playwright().start()
        match browser:
            case 'firefox':
                self.browser = self.pw.firefox.launch(headless=True)
            case 'edge':
                self.browser = self.pw.chromium.launch(headless=True)
            case 'chrome':
                self.browser = self.pw.chromium.launch(headless=True)
            case _:
                self.browser = self.pw.firefox.launch(headless=True)
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
         
    def get_website_html(self, url):
        custom_header = self.generate_header()
        page = self.browser.new_page(extra_http_headers=custom_header)
        response = page.goto(url)
        # page.wait_for_timeout(2000)
        # web_html_content = page.content()
        # page.close()
        # return web_html_content
        if response.status == 200:
            page.wait_for_timeout(2000)
            web_html_content = page.content()
            page.close()
            return web_html_content
        else:
            web_html_content = page.content()
            error_message = f'Error code {response.status}, {response.text()}, {web_html_content}'
            page.close()
            return error_message
    
    def get_website_content(self, url):
        html_content = self.get_website_html(url)
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

    def __del__(self):
        if self.destructor:
            self.browser.close()
            self.pw.stop()

class WebScraperSyncMultiBrowsers():
    def __init__(self, browser='firefox'):
        self.destructor = True
        if browser not in ['firefox', 'edge', 'chrome']:
            print(f'Browser {browser} is not supported')
            return None
        self.browser_type = browser
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
         
    def get_website_html(self, url):
        custom_header = self.generate_header()
        pw = sync_playwright().start()
        match self.browser_type:
            case 'firefox':
                browser = pw.firefox.launch(headless=True)
            case 'edge':
                browser = pw.chromium.launch(headless=True)
            case 'chrome':
                browser = pw.chromium.launch(headless=True)
            case _:
                browser = pw.firefox.launch(headless=True)
        page = browser.new_page(extra_http_headers=custom_header)
        response = page.goto(url)
        if response.status == 2000:
            page.wait_for_timeout(2000)
            web_html_content = page.content()
            page.close()
            browser.close()
            pw.stop()
            return web_html_content
        else:
            web_html_content = page.content()
            error_message = f'Error code {response.status}, {response.text()}, {web_html_content}'
            page.close()
            browser.close()
            pw.stop()
            return error_message
    
    def get_website_content(self, url):
        html_content = self.get_website_html(url)
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