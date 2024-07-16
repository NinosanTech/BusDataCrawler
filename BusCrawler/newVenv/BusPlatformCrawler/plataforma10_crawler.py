from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pandas import DataFrame as df
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import dateparser
import time
from BusPlatformCrawler.website_crawler_abstract import Crawler


class plataforma10_crawler(Crawler):

    NO_OPTIONS_CSS = "#root > div._1a87f7c14516a317eba6506a280b3a64-scss > div > div.bf8b6efd3c21a9fbf1f0d923e85f1adb-scss > div._10bdd5cf04aea1ec8560c0d855f7ede8-scss.b9f1b4b29f5f7a8a7213d59c69b7fa5d-scss > div"

    def __init__(self, origin_city: str, destination_city: str, date: str):
        super().__init__("https://www.plataforma10.com.ar/", origin_city, destination_city, date)

    def _pick_date(self, pick_date):
        calendar_months = self._d.find_elements(By.CLASS_NAME, "CalendarMonthGrid_month__horizontal")
        for month in calendar_months:
            for day in month.find_elements(By.CLASS_NAME, "CalendarDay"):
                if day.get_attribute("aria-disabled") == "false":
                    date = day.get_attribute("aria-label")
                    date_number = dateparser.parse(date)
                    if date_number == pick_date:
                        day.click()
                        return
        raise Exception("Date is not available")

    def _close_pop_up(self):
        try:
            pop_up_close = self._d.find_element(By.CLASS_NAME,"ant-modal-close")
            if pop_up_close != '':
                pop_up_close.click()
        except NoSuchElementException:
            pass
    
    def _select_origin(self) -> int:
        
        origin_field_css = "#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(1) > div > div > input"
        wait = WebDriverWait(self._d, 20)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, origin_field_css)))
        except TimeoutException:
            print(f"{self._main_logging_string}Origin selection field not found!", flush=True)
            return -1
        origin = self._d.find_element(By.CSS_SELECTOR, origin_field_css)
        origin.send_keys(self.origin_city)
        origin_selection_list = self._d.find_element(By.CSS_SELECTOR, '#react-autowhatever-1')
        try:
            wait.until(lambda d: origin_selection_list.get_attribute("class") != '')
        except TimeoutException: 
            print(f"{self._main_logging_string}Origin not available!", flush=True)
            return -2
        origin.send_keys(Keys.TAB)
        self.final_origin = origin.get_attribute("value")
        return 1

    def _select_destination(self) -> int:
        
        destination = self._d.find_element(By.CSS_SELECTOR, "#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(2) > div > div > input")
        destination.send_keys(self.destination_city)
        wait = WebDriverWait(self._d, 20)
        destination_selection_list = self._d.find_element(By.CSS_SELECTOR, '#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(2)').find_element(By.CSS_SELECTOR, '#react-autowhatever-1')
        try:
            wait.until(lambda d: destination_selection_list.get_attribute("class") != '')
        except TimeoutException: 
            print(f"{self._main_logging_string}Destination not available!", flush=True)
            return -3
        destination.send_keys(Keys.TAB)
        self.final_destination = destination.get_attribute("value")
        return 1

    def _select_date(self) -> int:
        
        wait = WebDriverWait(self._d, 20)
        date_selector = self._d.find_element(By.CSS_SELECTOR,'#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(3) > div > div > div > div > div')
        try:
            self._pick_date(dateparser.parse(self.date,date_formats=["%d/%m/%Y"]))
        except Exception:
            print(f"{self._main_logging_string}Date is not available!", flush=True)
            return None
        return 1

    def _click_search(self) -> int:
        self._d.find_element(By.ID, 'searchButton').click()
        wait = WebDriverWait(self._d, 60)
        try:
            wait.until(EC.any_of(EC.presence_of_element_located((By.CLASS_NAME, "b4eb40d73f2bd1854d3ed3c08c40fd97-scss")),\
                EC.presence_of_element_located((By.CSS_SELECTOR, self.NO_OPTIONS_CSS))\
                ))
        except TimeoutException:
            print(f"{self._main_logging_string}Search took too long!", flush=True)
            return -1
        try:
            no_options_text = self._d.find_element(By.CSS_SELECTOR, self.NO_OPTIONS_CSS).text
        except NoSuchElementException:
            return 1
        return -1
    
    def _scroll_to_element(self, actions: ActionChains, element) -> int:
        tries = 0
        while tries < 5:
            try:
                actions.scroll_to_element(element).perform()
                break
            except StaleElementReferenceException:
                tries = tries + 1
                time.sleep(1)
        else:
            print(f"{self._main_logging_string}Not possible to scroll to element!", flush=True)
            return None
        return 1
    
    def _extract_information(self, element, results: dict) -> dict:
        
        time_labels = element.find_elements(By.CLASS_NAME, '_6d00bee27a72edd32548abea2b556e38-scss')
        assert(len(time_labels) == 3)
        results["exits"].append(dateparser.parse(self._fix_date(time_labels[0].text)))
        results["arrivals"].append(dateparser.parse(self._fix_date(time_labels[1].text)))
        price_currency = element.find_element(By.CLASS_NAME, "d98c63988e78241604a17e69b6968da5-scss").text.split(" ")
        results["price"].append(price_currency[1])
        results["currency"].append(price_currency[0])
        results["availability"].append(element.find_element(By.CLASS_NAME, "b2c2207b019425d6282877959e004f79-scss").text)
        class_item = element.find_element(By.CLASS_NAME, "e209d44dc2f5e07f732ac5c780d0e322-scss").find_element(By.CLASS_NAME, "_0ce5bb5f30124c5cf7c74bce3784472e-scss")
        results["transportclass"].append(class_item.text)
        results["origin"].append(self.final_origin)
        results["destination"].append(self.final_destination)
        return results

    def check_location_availability(self) -> int:
        print(f"{self._main_logging_string}Searching on {self._url}:\n", flush=True)
        
        with self.connect_chrome() as self._d:
            self._d.get(self._url)
            print(self._d.title)

            self._close_pop_up()

            status = self._select_origin()
            if status != 1:
                return status

            status = self._select_destination()
            return status

    def retrieve_info(self) -> df:
        print(f"{self._main_logging_string}Searching on {self._url}:\n", flush=True)
        
        with self.connect_chrome() as self._d:
            self._d.get(self._url)
            print(self._d.title)

            self._close_pop_up()

            status = self._select_origin()
            if status != 1:
                return status

            status = self._select_destination()
            if status != 1:
                return status

            status = self._select_date()
            if status != 1:
                return status

            status = self._click_search()
            if status != 1:
                return status

            actions = ActionChains(self._d)
            results = self._build_result_dict()
            for i in self._d.find_elements(By.CLASS_NAME, "a4cbc503346125be234f811582ce0130-scss"):
                
                status = self._scroll_to_element(actions, i)
                if status != 1:
                    return status
                try:
                    results = self._extract_information(i, results)
                except Exception as e:
                    print(f"{self._main_logging_string}Information extraction failed!", flush=True)
                    return -1
                
            self.result_frame = df.from_dict(results)
            self._d.close()
            self.print_result()
            return self.result_frame