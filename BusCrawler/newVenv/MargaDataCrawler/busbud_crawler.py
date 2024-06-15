import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pandas import DataFrame as df
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.expected_conditions import element


url = "https://www.busbud.com/en"
origin_city = 'Buenos Aires'
destination_city = 'Salta'
date = "15/05/2024"

chrome_options = Options()
#chrome_options.add_argument("--headless")
d = webdriver.Chrome(options= chrome_options)
d.get(url)
origin = d.find_element(By.ID, "origin-city-input")
origin.send_keys(origin_city)
origin_selection_list = d.find_element(By.XPATH, '//*[@id="origin-city-input"]')
wait = WebDriverWait(d, 10)
wait.until(lambda d: origin_selection_list.get_attribute("aria-activedescendant") is not None)
origin.send_keys(Keys.TAB)
final_origin = d.find_element(By.CSS_SELECTOR,'#origin-dropdown-wrapper > div.t-18rc2c3-root-fullWidth-root > div > pre').get_attribute("innerHTML")

destination = d.find_element(By.ID, "destination-city-input")
destination.send_keys(destination_city)
wait = WebDriverWait(d, 10)
destination_selection_list = d.find_element(By.XPATH, '//*[@id="destination-city-input"]')
wait.until(lambda d: destination_selection_list.get_attribute("aria-activedescendant") is not None)
destination.send_keys(Keys.TAB)
final_destination = d.find_element(By.CSS_SELECTOR,'#destination-dropdown-wrapper > div.t-18rc2c3-root-fullWidth-root > div > pre').get_attribute("innerHTML")

wait = WebDriverWait(d, 10)
d.execute_script(f"arguments[0].value='{date}'",d.find_element(By.ID,'outbound-date-input'))
d.find_element(By.ID,'search-submit-button').click()
WebDriverWait(d, 10)
d.switch_to.window(d.window_handles[1])

actions = ActionChains(d)

results = {"exits": [], "arrivals": [], "price": [], "currency": []}
for i in d.find_elements(By.CSS_SELECTOR, '[data-cy-type="departure-card"]'):
    actions.scroll_to_element(i).perform()
    time_labels = i.find_elements(By.CLASS_NAME, 't-33cygo-DsLabel-root-DsLabel-sizeXl')
    assert(len(time_labels) == 2)
    results["exits"].append(time_labels[0].text)
    results["arrivals"].append(time_labels[1].text)
    results["price"].append(i.find_element(By.CLASS_NAME,"t-vpn5bl-DsLabel-root-DsLabel-sizeXl").text)
    results["currency"].append(i.find_element(By.CLASS_NAME,"t-180gaeg-DsLabel-root-DsLabel-sizeSm-currency").text)

result_frame = df.from_dict(results)
print(f"------------------\nOptions from {final_origin} to {final_destination} at {date}:\n")
print(result_frame)
print("\n------------------")
