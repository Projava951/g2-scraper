from bs4 import BeautifulSoup
from bose import BaseTask
from bose import BaseTask, Wait, Output, BrowserConfig
from selenium.webdriver.common.by import By
from bose.utils import merge_dicts_in_one_dict
from urllib.parse import urlparse, parse_qs

class Task(BaseTask):
    browser_config = BrowserConfig(use_undetected_driver=True, is_eager=True)
    def run(self, driver):
        links = []

        def htmltosoup(page):
            return BeautifulSoup(page, 'html.parser')

        def get_leaf_links(div):
            if(div.find_all("div", class_ = 'ml-2') == []):
                return [div.select_one('a[class$="link"]')['href']]

            leaf_links = []

            for div in div.find_all("div", class_ = 'ml-2'):
                leaf_links.extend(get_leaf_links(div))
            
            return leaf_links

        def get_category_links(input_categories):
            url = "https://www.g2.com/categories?view_hierarchy=true"
            driver.organic_get(url);

            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            driver.get_element_or_none_by_selector('div.newspaper-columns', Wait.VERY_LONG * 4)
            html = htmltosoup(driver.page_source)
            category_list = html.find_all("div", class_ = 'newspaper-columns__list-item pb-1')
            category_links = []
            for div in category_list:
                h2_name = div.select_one("h2").text
                is_exist = False

                for input_category in input_categories:
                    if (input_category == h2_name):
                        is_exist = True
                        break

                if (is_exist):
                    category_links.extend(get_leaf_links(div))
                        
            return category_links

        def get_page_count():
            el = driver.get_element_or_none_by_selector('#product-list  ul  li:last-child > a.pagination__named-link.js-log-click', Wait.SHORT)
            url = el.get_attribute("href")
            
            url_parts = urlparse(url)
            query_params = parse_qs(url_parts.query)

            # Extract the 'page' parameter from the query parameters
            page_number = query_params.get('page', [])[0]

            return int(page_number)

        def put_links():
            
            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            els = driver.get_elements_or_none_by_selector('[data-ordered-events-scope="products"][itemtype="http://schema.org/ListItem"]', Wait.VERY_LONG)

            def domap(el):
                href = el.find_element(By.CSS_SELECTOR, 'a.d-ib.c-midnight-100.js-log-click').get_attribute("href")
                return href

            result = list(map(domap, els))

            links.extend(result)
            
            return result

        input_categories = Output.read_pending()

        category_links = get_category_links(input_categories)

        for category_link in category_links:
            product_url = "https://www.g2.com" + category_link
            first= f"{product_url}#product-list"
            driver.organic_get(first)

            page_count = get_page_count()
            for next_page in range(2, page_count + 1):
                put_links()
                driver.short_random_sleep()
                driver.get_by_current_page_referrer(f"{self.product_url}?order=g2_score&page={next_page}#product-list" )
            put_links()
            print(links)
        
if __name__ == '__main__':
    Task().begin_task()