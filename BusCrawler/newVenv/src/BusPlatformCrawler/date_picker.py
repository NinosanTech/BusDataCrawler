from selenium import webdriver
from enum import Enum
import dateparser
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class Type(Enum):
    
    PLATAFORMA_10_OLD = 0
    PLATAFORMA_10_NEW = 1

class DatePicker():
    
    def __init__(self, driver: webdriver, calendar_type: Type, pick_date: datetime, logging_string: str):
        self._calendar_type = calendar_type
        self._d = driver
        self._date = pick_date
        self._main_logging_string = logging_string

    def pick_date(self):
        wait = WebDriverWait(self._d, 20)
        try:
            if self._calendar_type == Type.PLATAFORMA_10_OLD:
                date_selector = self._d.find_element(By.CSS_SELECTOR,'body > div.MuiPopper-root.MuiPickersPopper-root.mui-1mtsuo7 > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation8.MuiPickersPopper-paper.mui-4muze0 > div > div > div')
                self.pick_date_plat10_old()
            else:
                self.pick_date_plat10_new()
        except Exception:
            print(f"{self._main_logging_string}Date is not available!", flush=True)
            return None
        return 1

    def _find_current_month(self) -> datetime:
        month = self._d.find_element(By.CLASS_NAME,"mui-84dy3i")
        return dateparser.parse(month.text, date_formats=["%d/%m/%Y"])

    def pick_date_plat10_new(self):
        self._d.find_element(By.CSS_SELECTOR, "body > main > div > section.home_search-and-slider-container__he1xt > section.home_search-container__msbdB > div > div > div.SearchBox_search-box-item__EwzeE.SearchBox_half-width__DuL4h > div.SearchBox_departureContainer__n5Lpz > div > div > div > button").click()
        current_month = self._find_current_month()
        while current_month.month != self._date.month or current_month.year != self._date.year:
            self._d.find_element(By.CSS_SELECTOR, "body > div.MuiPopper-root.MuiPickersPopper-root.mui-1mtsuo7 > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation8.MuiPickersPopper-paper.mui-4muze0 > div > div > div > div.mui-84dy3i > div > div:nth-child(2) > button").click()
            current_month = self._find_current_month()
        calendar = self._d.find_element(By.CLASS_NAME, "MuiDayCalendar-monthContainer")
        days = calendar.find_elements(By.CSS_SELECTOR, "*")
        for day in days:
            if day.get_attribute("class") == "MuiTouchRipple-root mui-w0pj6f":
                day_value = day.find_element(By.XPATH, "..")
                if self._date.day == dateparser.parse(day_value.text, date_formats=["%d"]).day:
                    day_value.click()
                    return
        raise Exception("Date is not available")

    def pick_date_plat10_old(self):
        calendar_months = self._d.find_elements(By.CLASS_NAME, "CalendarMonthGrid_month__horizontal")
        for month in calendar_months:
            for day in month.find_elements(By.CLASS_NAME, "CalendarDay"):
                if day.get_attribute("aria-disabled") == "false":
                    date = day.get_attribute("aria-label")
                    date_number = dateparser.parse(date)
                    if date_number == self._date:
                        day.click()
                        return
        raise Exception("Date is not available")
