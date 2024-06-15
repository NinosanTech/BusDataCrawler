import requests
#from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pandas import DataFrame as df
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import dateparser
import geonamescache
import itertools
import time

def get_cities(country_code: str) -> list:
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()
    return_cities = []
    for key in cities:
        cities_for_key = cities[key]
        if cities_for_key['countrycode'] == country_code:
            city_name = cities_for_key['name']
            if city_name not in return_cities:
                return_cities.append(city_name)
    return return_cities

def select_date(driver, pick_date):
    calendar_months = driver.find_elements(By.CLASS_NAME, "CalendarMonthGrid_month__horizontal")
    for month in calendar_months:
        for day in month.find_elements(By.CLASS_NAME, "CalendarDay"):
            if day.get_attribute("aria-disabled") == "false":
                date = day.get_attribute("aria-label")
                date_number = dateparser.parse(date)
                if date_number == pick_date:
                    day.click()
                    return
    raise Exception("Date is not available")

def main(origin_city: str, destination_city: str, date: str) -> df:
    url = "https://www.plataforma10.com.ar/"
    #origin_city = 'Mendoza'
    #destination_city = 'Salta'
    #date = "18/05/2024"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    d = webdriver.Chrome(options= chrome_options)
    d.get(url)

    pop_up_close = d.find_element(By.CLASS_NAME,"ant-modal-close")
    if pop_up_close != '':
        pop_up_close.click()

    origin = d.find_element(By.CSS_SELECTOR, "#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(1) > div > div > input")
    origin.send_keys(origin_city)
    origin_selection_list = d.find_element(By.CSS_SELECTOR, '#react-autowhatever-1')
    wait = WebDriverWait(d, 10)
    try:
        wait.until(lambda d: origin_selection_list.get_attribute("class") != '')
    except TimeoutException: 
        print("Origin not available!")
        return
    origin.send_keys(Keys.TAB)
    final_origin = origin.get_attribute("value")

    destination = d.find_element(By.CSS_SELECTOR, "#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(2) > div > div > input")
    destination.send_keys(destination_city)
    wait = WebDriverWait(d, 10)
    destination_selection_list = d.find_element(By.CSS_SELECTOR, '#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(2)').find_element(By.CSS_SELECTOR, '#react-autowhatever-1')
    try:
        wait.until(lambda d: destination_selection_list.get_attribute("class") != '')
    except TimeoutException: 
        print("Destination not available!")
        return
    destination.send_keys(Keys.TAB)
    final_destination = destination.get_attribute("value")

    wait = WebDriverWait(d, 10)
    date_selector = d.find_element(By.CSS_SELECTOR,'#form > div.b5aeccc22403454d888b73014424ee13-scss > div:nth-child(3) > div > div > div > div > div')
    try:
        select_date(d, dateparser.parse(date))
    except Exception:
        print("Date is not available!")
        return
    #d.execute_script(f"arguments[0].value='{date}'", date_selector.find_element(By.CSS_SELECTOR, "#date"))
    actions = ActionChains(d)
    #actions.move_to_element_with_offset(destination, 0, 50).click().perform()

    d.find_element(By.ID, 'searchButton').click()
    wait = WebDriverWait(d, 10)
    try:
        wait.until(lambda d: d.find_element(By.CLASS_NAME, "b4eb40d73f2bd1854d3ed3c08c40fd97-scss") != '')
    except TimeoutException:
        print("Search took too long or no options found!")
        return None
    #d.switch_to.window(d.window_handles[1])



    results = {"exits": [], "arrivals": [], "price": [], "currency": [], "availability": [], "class": [], "from": [], "to": []}
    for i in d.find_elements(By.CLASS_NAME, "a4cbc503346125be234f811582ce0130-scss"):
        tries = 0
        while tries < 5:
            try:
                actions.scroll_to_element(i).perform()
                break
            except StaleElementReferenceException:
                tries = tries + 1
                time.sleep(1)
        else:
            print("Not possible to scroll to element!")
            return None

        time_labels = i.find_elements(By.CLASS_NAME, '_6d00bee27a72edd32548abea2b556e38-scss')
        assert(len(time_labels) == 3)
        results["exits"].append(dateparser.parse(time_labels[0].text.replace('hs','')))
        results["arrivals"].append(dateparser.parse(time_labels[1].text.replace('hs','')))
        price_currency = i.find_element(By.CLASS_NAME, "d98c63988e78241604a17e69b6968da5-scss").text.split(" ")
        results["price"].append(price_currency[1])
        results["currency"].append(price_currency[0])
        results["availability"].append(i.find_element(By.CLASS_NAME, "b2c2207b019425d6282877959e004f79-scss").text)
        class_item = i.find_element(By.CLASS_NAME, "e209d44dc2f5e07f732ac5c780d0e322-scss").find_element(By.CLASS_NAME, "_0ce5bb5f30124c5cf7c74bce3784472e-scss")
        results["class"].append(class_item.text)
        results["from"].append(final_origin)
        results["to"].append(final_destination)

    result_frame = df.from_dict(results)
    print(f"------------------\nOptions from {final_origin} to {final_destination} at {date}:\n")
    print(result_frame)
    print("\n------------------")
    return result_frame

cities = get_cities('AR')
cities_combinations = []
for i in range(len(cities)):
    for j in range(len(cities)):
        if i != j:
            cities_combinations.append((cities[i], cities[j]))
date = "18/05/2024"
results = []
for comb in cities_combinations:
    print(f"Searching from {comb[0]} to {comb[1]}:\n")
    new_result = main(comb[0], comb[1], date)
    if new_result is None or (type(new_result) is list and new_result[0] is None):
        continue
    if len(results) == 0:
        results = pd.concat([new_result])
    else:
        results = pd.concat([results,new_result])

print(results)