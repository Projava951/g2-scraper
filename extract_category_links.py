from bs4 import BeautifulSoup
from bose import BaseTask
from bose import BaseTask, Wait, Output, BrowserConfig
from bose.utils import merge_dicts_in_one_dict

class Task(BaseTask):
    browser_config = BrowserConfig(use_undetected_driver=True, is_eager=True)
    def run(self, driver):

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
                        
            print(category_links)
            return "asdf"

        input_categories = Output.read_pending()

        get_category_links(input_categories)
        
if __name__ == '__main__':
    Task().begin_task()