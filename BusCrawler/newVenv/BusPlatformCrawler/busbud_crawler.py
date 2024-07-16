import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pandas import DataFrame as df
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from BusPlatformCrawler.website_crawler_abstract import Crawler


class BusBudCrawler(Crawler):

    def __init__(self, origin_city: str, destination_city: str, date: str):
        super().__init__("https://www.busbud.com/en", origin_city, destination_city, date)
    
    def _select_origin(self) -> int:

        origin = self._d.find_element(By.ID, "origin-city-input")
        origin.send_keys(self.origin_city)
        origin_selection_list = self._d.find_element(By.XPATH, '//*[@id="origin-city-input"]')
        wait = WebDriverWait(self._d, 30)
        try:
            wait.until(lambda d: origin_selection_list.get_attribute("aria-activedescendant") is not None)
        except TimeoutException:
            print(f"{self._main_logging_string}Origin not available!", flush=True)
            return -2
        origin.send_keys(Keys.TAB)
        self.final_origin = self._d.find_element(By.CSS_SELECTOR,'#origin-dropdown-wrapper > div.t-18rc2c3-root-fullWidth-root > div > pre').get_attribute("innerHTML")
        return 1
    
    def _select_destination(self) -> int:
        
        destination = self._d.find_element(By.ID, "destination-city-input")
        destination.send_keys(self.destination_city)
        wait = WebDriverWait(self._d, 30)
        destination_selection_list = self._d.find_element(By.XPATH, '//*[@id="destination-city-input"]')
        try:
            wait.until(lambda d: destination_selection_list.get_attribute("aria-activedescendant") is not None)
        except TimeOutException:
            print(f"{self._main_logging_string}Destination not available!", flush=True)
            return -3
        destination.send_keys(Keys.TAB)
        self.final_destination = self._d.find_element(By.CSS_SELECTOR,'#destination-dropdown-wrapper > div.t-18rc2c3-root-fullWidth-root > div > pre').get_attribute("innerHTML")
        return 1

    def _select_date(self) -> int:
        wait = WebDriverWait(self._d, 30)
        self._d.execute_script(f"arguments[0].value='{self.date}'",self._d.find_element(By.ID,'outbound-date-input'))
        return 1

    def _extract_information(self, element, results: dict) -> dict:
        actions.scroll_to_element(element).perform()
        time_labels = element.find_elements(By.CLASS_NAME, 't-33cygo-DsLabel-root-DsLabel-sizeXl')
        assert(len(time_labels) == 2)
        results["exits"].append(time_labels[0].text)
        results["arrivals"].append(time_labels[1].text)
        results["price"].append(element.find_element(By.CLASS_NAME,"t-vpn5bl-DsLabel-root-DsLabel-sizeXl").text)
        results["currency"].append(element.find_element(By.CLASS_NAME,"t-180gaeg-DsLabel-root-DsLabel-sizeSm-currency").text)
        results["availability"].append(None)
        results["transportclass"].append(None)
        results["origin"].append(self.final_origin)
        results["destination"].append(self.final_destination)
        return results

    def retrieve_info(self) -> df:
        print(f"{self._main_logging_string}Searching on {self._url}:\n", flush=True)
        
        with self.connect_chrome() as self._d:
            self._d.get(self._url)
            print(self._d.title)

            status = self._select_origin()
            if status != 1:
                return status

            status = self._select_destination()
            if status != 1:
                return status

            status = self._select_date()
            if status != 1:
                return status
        
            self._d.find_element(By.ID,'search-submit-button').click()
            wait = WebDriverWait(self._d, 30)
            try:
                wait.until(len(self._d.window_handles) > 1)
            except TimeOutException:
                print(f"{self._main_logging_string}Search went wrong. No new window opened!", flush=True)
                return -1

            self._d.switch_to.window(self._d.window_handles[1])
            wait = WebDriverWait(self._d, 60)
            try:
                wait.until()
            except TimeOutException:
                print(f"{self._main_logging_string}Result page did not load in time!", flush=True)
                return -1

            actions = ActionChains(d)
            results = self._build_result_dict()
            for i in d.find_elements(By.CSS_SELECTOR, '[data-cy-type="departure-card"]'):
                try:
                    results = self._extract_information(i, results)
                except Exception as e:
                    print(f"{self._main_logging_string}Information extraction failed!", flush=True)
                    return -1
            self.result_frame = df.from_dict(results)
            self._d.close()
            self.print_result()
            return self.result_frame

    def check_location_availability(self):
        pass