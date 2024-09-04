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
from BusPlatformCrawler.date_picker import DatePicker, Type


class plataforma10_crawler(Crawler):

    NO_OPTIONS_CSS = "body > main > div > section.SimpleMainSearch_results-data-container__zna0O > section > div.SimpleMainSearch_empty-services-container__lAxqL > div > div > h2"
    DAY_SELECTION_IDENTIFICATION = "4px solid rgb(255, 119, 49)"

    def __init__(self, origin_city: str, destination_city: str, date: str):
        super().__init__("https://www.plataforma10.com.ar/", origin_city, destination_city, date)

    def _close_pop_up(self):
        try:
            pop_up_close = self._d.find_element(By.CLASS_NAME,"ant-modal-close")
            if pop_up_close != '':
                pop_up_close.click()
        except NoSuchElementException:
            pass
    
    def _select_origin(self) -> int:        
        origin_field_css = "#origin-input"
        wait = WebDriverWait(self._d, 20)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, origin_field_css)))
        except TimeoutException:
            print(f"{self._main_logging_string}Origin selection field not found!", flush=True)
            return -1
        origin = self._d.find_element(By.CSS_SELECTOR, origin_field_css)
        origin.send_keys(self.origin_city)
        try:
            wait.until(lambda d: origin.get_attribute("aria-controls") != None)
        except TimeoutException: 
            print(f"{self._main_logging_string}Origin not available!", flush=True)
            return -2
        origin.send_keys(Keys.ARROW_DOWN)
        origin.send_keys(Keys.ENTER)
        self.final_origin = origin.get_attribute("value")
        return 1

    def _select_destination(self) -> int:
        destination_field_css = "#destination-input"
        destination = self._d.find_element(By.CSS_SELECTOR, destination_field_css)
        destination.send_keys(self.destination_city)
        wait = WebDriverWait(self._d, 20)
        try:
            wait.until(lambda d: destination.get_attribute("aria-controls") != None)
        except TimeoutException: 
            print(f"{self._main_logging_string}Destination not available!", flush=True)
            return -3
        destination.send_keys(Keys.ARROW_DOWN)
        destination.send_keys(Keys.ENTER)
        self.final_destination = destination.get_attribute("value")
        return 1

    def _wait_for_results(self, wait: WebDriverWait) -> int:
        try:
            wait.until(EC.any_of(\
                EC.all_of(EC.invisibility_of_element((By.CLASS_NAME, "PageLoading_container__oGMv1")),\
                    EC.presence_of_element_located((By.CLASS_NAME, "SimpleMainSearch_search-result-list__CKKcn"))),\
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

    def _click_search(self) -> int:
        self._d.find_element(By.CSS_SELECTOR, 'body > main > div > section.home_search-and-slider-container__he1xt > section.home_search-container__msbdB > div > div > div.SearchBox_search-box-item__EwzeE.SearchBox_search-button__To5kM > button') \
            .click()
        wait = WebDriverWait(self._d, 60)
        return self._wait_for_results(wait)
    
    def _scroll_to_element(self, actions: ActionChains, element) -> int:
        tries = 0
        while tries < 10:
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
    
    def _select_next_day(self) -> int:
        day_buttons = self._d.find_element(By.CLASS_NAME,"OtherDates_other-dates__HxaTs")
        day_selectors = day_buttons.find_elements(By.CLASS_NAME, "Button_alternative__EqR30")
        for i,selector in enumerate(day_selectors):
            if selector.get_attribute("class").find("Button_primary__DEC_1") != -1:
                day_selectors[i+1].click()
                break
        time.sleep(1)
        wait = WebDriverWait(self._d, 60)
        return self._wait_for_results(wait)

    def _extract_information(self, element, results: dict) -> dict:
        
        results["exits"].append(dateparser.parse(self._fix_date(element.find_element(By.CLASS_NAME, "searchResultCard_departure-date__MLSWd").text)))
        results["arrivals"].append(dateparser.parse(self._fix_date(element.find_element(By.CLASS_NAME, "searchResultCard_arrival-date__eVVbj").text)))
        price_currency = element.find_element(By.CLASS_NAME, "searchResultCard_card__price-and-currency__nyZXT").text.split("\n")
        results["price"].append(price_currency[1])
        results["currency"].append(price_currency[0])
        results["availability"].append(element.find_elements(By.CLASS_NAME, "searchResultCard_card__info-text__6FKWE")[1].text.replace("Pasajes ", ""))
        results["company"].append(element.find_element(By.CLASS_NAME, "searchResultCard_card__company__zrAtx").text)
        class_item = element.find_element(By.CLASS_NAME, "searchResultCard_card__quality-text__O2xs0")
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

            date_picker = DatePicker(self._d, Type.PLATAFORMA_10_NEW, \
                dateparser.parse(self.date, date_formats=["%d/%m/%Y"]), \
                    self._main_logging_string)
            status = date_picker.pick_date()
            if status != 1:
                return status

            no_result_ctr = 0
            status = self._click_search()
            if status == -1:
                no_result_ctr = no_result_ctr + 1

            actions = ActionChains(self._d)
            results = self._build_result_dict()
            for i_day_advance in range(0,4):
                for i in self._d.find_elements(By.CLASS_NAME, "searchResultCard_card__5Avpr"):
                    
                    status = self._scroll_to_element(actions, i)
                    if status != 1:
                        return status
                    try:
                        results = self._extract_information(i, results)
                    except Exception as e:
                        print(f"{self._main_logging_string}Information extraction failed!", flush=True)
                        return 1
                status = self._select_next_day()
                if status != 1:
                    no_result_ctr = no_result_ctr + 1
            self._d.close()
            if len(results['exits']) == 0:
                return no_result_ctr
            self.result_frame = df.from_dict(results)
            self.print_result()
            return self.result_frame