from bs4 import BeautifulSoup
from bose import BaseTask
from bose import BaseTask, Wait, Output, BrowserConfig
from selenium.webdriver.common.by import By
from bose.utils import merge_dicts_in_one_dict
from urllib.parse import urlparse, parse_qs

class Task(BaseTask):
    browser_config = BrowserConfig(use_undetected_driver=True, is_eager=True)
    input_category = ""
    def run(self, driver):
        links = []

        def htmltosoup(page):
            return BeautifulSoup(page, 'html.parser')

        def get_company_data(company_url):
            driver.organic_get(company_url)
            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            driver.get_element_or_none_by_selector('h1.l2.pb-half.inline-block', Wait.VERY_LONG * 4)
            html = htmltosoup(driver.page_source)

            input_category = self.input_category
            ol_ele = html.select_one('ol[id$="breadcrumbs"]')
            li_eles = ol_ele.find_all("li", itemprop = 'itemListElement')

            return li_eles

        data = get_company_data("https://www.g2.com/products/consensus/reviews")
        print(data)
        
if __name__ == '__main__':
    Task().begin_task()