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
                p_div = p
                p.find("div", class_ = 'fw-semibold').decompose()
                link = p.find("a", class_ = 'link')
            
                if link is not None:
                    if link.text == "www.linkedin.com":
                        p = link['href'] + "||" + p_div.text
                    else:
                        p = link['href']
                else:
                    data = str(p)
                    
                    if 'Twitter' in data:
                        p =  data.replace('<div class="ml-1">', '').replace('</div>', '').replace('<br/>', ' ').strip()
                    else:
                        p = p.text
            
                details_values.append(p)

            details = dict(zip(details_titles, details_values))

            if "Website" in details:
                website = details["Website"]
            else:
                website = ""

            review_div = html.select_one('div[id$="reviews"]')
            rate_count_h3 = review_div.find_all("h3")[0]

            try: 
                rate_count = rate_count_h3.text.split(" ")[0]
            except AttributeError:
                rate_count = ""

            rating_span = review_div.find_all("span", class_="fw-semibold")[0]        
            try: 
                rating = rating_span.text.strip()
            except AttributeError:
                rating = ""

            if "Seller" in details:
                vendor_name = details["Seller"]
            else:
                vendor_name = ""
            
            if "LinkedIn Page" in details:
                if len(details["LinkedIn Page"].split("||")) > 0:
                    linkedin_profile = details["LinkedIn Page"].split("||")[0]
                    linkedin_follow_count = details["LinkedIn Page"].split("||")[1].split(" ")[0].split(".com")[1]
                else:
                    linkedin_profile = details["LinkedIn Page"].split("||")[0]
                    linkedin_follow_count = ""
            else:
                linkedin_profile = ""
                linkedin_follow_count = ""

            if "HQ Location" in details:
                hq_location = details["HQ Location"]
            else:
                hq_location = ""

            if "Twitter" in details:
                if len(details["Twitter"].split(" ")) > 0:
                    twitter_profile = details["Twitter"].split(" ")[0]
                    twitter_follow_count = details["Twitter"].split(" ")[1]
                else:
                    twitter_profile = details["Twitter"].split(" ")[0]
                    twitter_follow_count = ""
            else:
                twitter_profile = ""
                twitter_follow_count = ""

            ul_high_rated_features = html.find_all("ul", class_="list--chevron")[0]
            if ul_high_rated_features == None:
                high_rated_features_1 = ""
                high_rated_features_2 = ""
                high_rated_features_3 = ""
            else:
                li_high_rated_features = ul_high_rated_features.find_all("li", class_="fw-semibold")
                try: 
                    high_rated_features_1 = li_high_rated_features[0].text.split(" - ")[0]
                except AttributeError:
                    high_rated_features_1 = ""

                try: 
                    high_rated_features_2 = li_high_rated_features[1].text.split(" - ")[0]
                except AttributeError:
                    high_rated_features_2 = ""

                try: 
                    high_rated_features_3 = li_high_rated_features[2].text.split(" - ")[0]
                except AttributeError:
                    high_rated_features_3 = ""

            user_rating_div = html.select_one('div[data-equalizer$="measure-title"]')
            if user_rating_div == None:
                ease_of_use = ""
                quality_of_support = ""
                ease_of_setup = ""
            else:
                user_rating_div_children = user_rating_div.find_all("div", class_="center-center")
                ease_of_use = user_rating_div_children[0].text
                quality_of_support = user_rating_div_children[1].text
                ease_of_setup = user_rating_div_children[2].text

            features_url = company_url.replace("/reviews", "/features")
            driver.organic_get(features_url)
            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            driver.get_element_or_none_by_selector('h1.l2.pb-half.inline-block', Wait.VERY_LONG * 4)
            html = htmltosoup(driver.page_source)

            features_summary_div = html.select_one('div[class$="paper paper--box"]')
            features_h3s = features_summary_div.find_all("h3", class_="14")
            features_uls = features_summary_div.find_all("ul", class_="list--checked")

            try: 
                feature_1 = features_h3s[0].text + " > " + features_uls[0].find_all("li")[0].text
            except AttributeError:
                feature_1 = ""

            try: 
                feature_2 = features_h3s[1].text + " > " + features_uls[1].find_all("li")[0].text
            except AttributeError:
                feature_2 = ""

            try: 
                feature_3 = features_h3s[2].text + " > " + features_uls[2].find_all("li")[0].text
            except AttributeError:
                feature_3 = ""

            try: 
                feature_4 = features_h3s[3].text + " > " + features_uls[3].find_all("li")[0].text
            except AttributeError:
                feature_4 = ""

            try: 
                feature_5 = features_h3s[4].text + " > " + features_uls[4].find_all("li")[0].text
            except AttributeError:
                feature_5 = ""

            try: 
                feature_6 = features_h3s[5].text + " > " + features_uls[5].find_all("li")[0].text
            except AttributeError:
                feature_6 = ""

            try: 
                feature_7 = features_h3s[6].text + " > " + features_uls[6].find_all("li")[0].text
            except AttributeError:
                feature_7 = ""


            print(feature_1)
            print(feature_2)
            print(feature_3)
            print(feature_4)
            print(feature_5)
            print(feature_6)
            print(feature_7)

            return li_eles

        data = get_company_data("https://www.g2.com/products/consensus/reviews")
        
if __name__ == '__main__':
    Task().begin_task()