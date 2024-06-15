import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


url = "https://taqsa.centraldepasajes.com.ar/agenciaframe.aspx?Token=ef3L5LBPbYtUHwIcq2itS6w7q3icyGvlof%2beQwB9Y%2f0%3d&age=taq"

chrome_options = Options()
chrome_options.add_argument("--headless")
d = webdriver.Chrome(options= chrome_options)
d.get(url)
d.find_element(By.ID, "Origen").send_keys('Los Antiguos')

destination = d.find_element(By.ID, "Destino")
destination.send_keys('Esquel')
destination.send_keys(Keys.TAB)
d.execute_script("arguments[0].value='03/04/2024'",d.find_element(By.ID,'datepicker-ida'))
d.find_element(By.ID,'btnCons').click()
WebDriverWait(d, 3000)
d.switch_to.window(d.window_handles[1])
exits =  []
arrivals =  []
price = []
for i in d.find_element(By.ID, "servicios").find_elements(By.ID,"divData"):
    exits.append(i.find_element(By.XPATH, '//*[@id="divData"]/div[1]/div[1]/div[2]').text)
    arrivals.append(i.find_element(By.XPATH, '//*[@id="divData"]/div[1]/div[3]/div[2]').text)
    price.append(i.find_element(By.CLASS_NAME, "valor").text)