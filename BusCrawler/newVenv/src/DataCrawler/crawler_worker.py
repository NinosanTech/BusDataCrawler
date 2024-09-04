from BusPlatformCrawler.plataforma10_crawler import plataforma10_crawler
from BusPlatformCrawler.website_crawler_abstract import Debug
import logging
from enum import Enum

class Worker_Type(Enum):
    
    CRAWL = 0
    CHECK_LOCATIONS = 1


class Worker():
    def __init__(self, debug: Debug, worker_type: Worker_Type):
        self.debug = debug
        self.worker_type = worker_type

    def run(self, args) -> list:
        try:
            start_message = f"Worker started for {args}"
            logging.info(start_message)
            crawler = plataforma10_crawler(*args[1:])
            crawler.debug = self.debug
            if self.worker_type == Worker_Type.CRAWL:
                result = crawler.retrieve_info()
            elif self.worker_type == Worker_Type.CHECK_LOCATIONS:
                result = crawler.check_location_availability()
            end_message = f"Worker finished for {args}"
            logging.info(end_message)
            return [result, args]
        except Exception as e:
            print(f"Error: {e}", flush=True)
            return args