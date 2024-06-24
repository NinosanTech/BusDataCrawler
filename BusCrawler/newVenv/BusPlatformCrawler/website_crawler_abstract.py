from abc import ABC, abstractmethod
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from enum import Enum
from pandas import DataFrame as df
from BusPlatformCrawler.proxy_extension import proxies
from BusPlatformCrawler import credentials

class Debug(Enum):
    
    NO_DEBUG = 0
    LOCAL_SELENIUM_CONTAINER = 1
    LOCAL_CHROME_INSTANCE = 2
    AZURE_DEPLOY = 3

class Crawler(ABC):

    def __init__(self, url: str, origin_city: str, destination_city:str, date: str):
        self._url = url
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.date = date
        self._main_logging_string = f"[{self.origin_city} to {self.destination_city}]: "
        self.result_frame = None
        self.final_origin = None
        self.final_destination = None
        self.debug = Debug.NO_DEBUG

    @abstractmethod
    def retrieve_info() -> df:
        pass

    def _build_result_dict(self) -> dict:
        return {"exits": [], "arrivals": [], "price": [], "currency": [], "availability": [], "transportclass": [], "origin": [], "destination": []}
    
    def connect_chrome(self):
        chrome_options = Options()
        # headless does not work with proxy!
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('log-level=1')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        username = credentials.proxy_username
        password = credentials.proxy_password
        endpoint = '185.199.229.156'
        port = '7492'
        proxies_extension = proxies(username, password, endpoint, port)
        chrome_options.add_extension(proxies_extension)
        
        if self.debug == Debug.NO_DEBUG:
            driver = webdriver.Remote('http://selenium:4444/wd/hub', options=chrome_options)
        elif self.debug == Debug.LOCAL_SELENIUM_CONTAINER or self.debug == Debug.AZURE_DEPLOY:
            driver = webdriver.Remote('http://localhost:4444', options=chrome_options)
        elif self.debug == Debug.LOCAL_CHROME_INSTANCE:
            driver = webdriver.Chrome(options= chrome_options)
            
        return driver

    def _fix_date(self, date: str) -> str:
        return date.replace('Mar','Martes').replace('hs','')

    def print_result(self):
        print(f"------------------\nOptions from {self.final_origin} to {self.final_destination} at {self.date}:\n", flush=True)
        print(self.result_frame, flush=True)
        print("\n------------------", flush=True)