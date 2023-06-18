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
            all_categories = ""
            for i in range(len(li_eles)):
                if (i > 0 and i < len(li_eles) - 1):
                    if (i == len(li_eles) - 2):
                        all_categories += li_eles[i].select_one('span[itemprop$="name"]').text
                    else:
                        all_categories += li_eles[i].select_one('span[itemprop$="name"]').text + ' | '

            company_link = company_url
            title_div = html.select_one('div[class$="product-head__title"]')
            title = title_div.select_one('div[itemprop$="name"]').select_one('a').text

            details_list = html.find_all("div", class_ = 'ml-1')

            
            details_titles = ['LinkedIn Page' if 'LinkedIn' in p.next.text and 'Page' in p.next.text else  p.next.text for p in details_list]

            details_values = []
            
            for p in details_list:
                
                p.find("div", class_ = 'fw-semibold').decompose()
                link = p.find("a", class_ = 'link')
            
                if link is not None:
                    p = link['href']
                else:
                    data = str(p)
                    
                    if 'Twitter' in data:
                        p =  data.replace('<div class="ml-1">', '').replace('</div>', '').replace('<br/>', ' ').strip()
                    else:
                        p = p.text
            
                details_values.append(p)

            details = dict(zip(details_titles, details_values))

            print(details)

            return li_eles

        data = get_company_data("https://www.g2.com/products/consensus/reviews")
        print(data)
        
if __name__ == '__main__':
    Task().begin_task()