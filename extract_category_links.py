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
            try: 
                url = el.get_attribute("href")
            
                url_parts = urlparse(url)
                query_params = parse_qs(url_parts.query)

                # Extract the 'page' parameter from the query parameters
                page_number = query_params.get('page', [])[0]
            except AttributeError:
                page_number = "1"

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

        def get_company_data(company_url, input_category):
            driver.organic_get(company_url)
            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            driver.get_element_or_none_by_selector('h1.l2.pb-half.inline-block', Wait.VERY_LONG * 4)
            html = htmltosoup(driver.page_source)

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
                if len(details["LinkedIn Page"].split("||")) > 1:
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
                if len(details["Twitter"].split(" ")) > 1:
                    twitter_profile = details["Twitter"].split(" ")[0]
                    twitter_follow_count = details["Twitter"].split(" ")[1]
                else:
                    twitter_profile = details["Twitter"].split(" ")[0]
                    twitter_follow_count = ""
            else:
                twitter_profile = ""
                twitter_follow_count = ""

            ul_high_rated_features = html.find_all("ul", class_="list--chevron")
            if ul_high_rated_features == []:
                high_rated_features_1 = ""
                high_rated_features_2 = ""
                high_rated_features_3 = ""
            else:
                li_high_rated_features = ul_high_rated_features[0].find_all("li", class_="fw-semibold")
                try: 
                    high_rated_features_1 = li_high_rated_features[0].text.split(" - ")[0]
                except IndexError:
                    high_rated_features_1 = ""

                try: 
                    high_rated_features_2 = li_high_rated_features[1].text.split(" - ")[0]
                except IndexError:
                    high_rated_features_2 = ""

                try: 
                    high_rated_features_3 = li_high_rated_features[2].text.split(" - ")[0]
                except IndexError:
                    high_rated_features_3 = ""

            user_rating_div = html.select_one('div[data-equalizer$="measure-title"]')
            if user_rating_div == None:
                ease_of_use = ""
                quality_of_support = ""
                ease_of_setup = ""
            else:
                user_rating_div_children = user_rating_div.find_all("div", class_="center-center")
                try: 
                    ease_of_use = user_rating_div_children[0].text
                except IndexError:
                    ease_of_use = ""
                
                try: 
                    quality_of_support = user_rating_div_children[1].text
                except IndexError:
                    quality_of_support = ""

                try: 
                    ease_of_setup = user_rating_div_children[2].text
                except IndexError:
                    ease_of_setup = ""

            features_url = company_url.replace("/reviews", "/features")
            driver.organic_get(features_url)
            if driver.is_bot_detected():
              driver.wait_for_enter("Bot has been detected. Solve it to continue.")
            else: 
                print("Not Detected")

            driver.get_element_or_none_by_selector('h1.l2.pb-half', Wait.VERY_LONG * 4)
            html = htmltosoup(driver.page_source)

            features_summary_div = html.select_one('div[class$="paper paper--box"]')
            features_h3s = features_summary_div.find_all("h3")
            features_uls = features_summary_div.find_all("ul", class_="list--checked")

            try: 
                feature_1 = features_h3s[0].text + " > " + features_uls[0].find_all("li")[0].text
            except IndexError:
                feature_1 = ""

            try: 
                feature_2 = features_h3s[1].text + " > " + features_uls[1].find_all("li")[0].text
            except IndexError:
                feature_2 = ""

            try: 
                feature_3 = features_h3s[2].text + " > " + features_uls[2].find_all("li")[0].text
            except IndexError:
                feature_3 = ""

            try: 
                feature_4 = features_h3s[3].text + " > " + features_uls[3].find_all("li")[0].text
            except IndexError:
                feature_4 = ""

            try: 
                feature_5 = features_h3s[4].text + " > " + features_uls[4].find_all("li")[0].text
            except IndexError:
                feature_5 = ""

            try: 
                feature_6 = features_h3s[5].text + " > " + features_uls[5].find_all("li")[0].text
            except IndexError:
                feature_6 = ""

            try: 
                feature_7 = features_h3s[6].text + " > " + features_uls[6].find_all("li")[0].text
            except IndexError:
                feature_7 = ""

            details = {
                'Input Category 1': input_category,
                'All categories': all_categories,
                'Company link': company_link,
                'Title': title,
                'Website': website,
                'Nr of ratings': rate_count,
                'Rating': rating,
                'Vendor name': vendor_name,
                'Linkedin Nr of employees': linkedin_follow_count,
                'Linkedin profile': linkedin_profile,
                'HQ location': hq_location,
                'Twitter profile': twitter_profile,
                'Twitter followers': twitter_follow_count,
                'Highest rated features 1': high_rated_features_1,
                'Highest rated features 2': high_rated_features_2,
                'Highest rated features 3': high_rated_features_3,
                'Ease of use': ease_of_use,
                'Quality of support': quality_of_support,
                'Ease of setup': ease_of_setup,
                'Features 1': feature_1,
                'Features 2': feature_2,
                'Features 3': feature_3,
                'Features 4': feature_4,
                'Features 5': feature_5,
                'Features 6': feature_6,
                'Features 7': feature_7
            }

            return details

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
                driver.get_by_current_page_referrer(f"{product_url}?order=g2_score&page={next_page}#product-list" )
            put_links()
        
        result = []
        for link in links:
            data = get_company_data(link, input_categories[0])
            result.append(data)
        Output.write_csv(result, "finished.csv")
        
if __name__ == '__main__':
    Task().begin_task()