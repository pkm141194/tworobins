from selenium import webdriver
from datetime import datetime
from  time import sleep
from Functions import clean_text, clean_price
import logging
import sys
import bs4
import urllib
import urllib3
import os
from requests_html import HTMLSession

urllib3.disable_warnings()
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")

#System.setProperty("webdriver.gecko.driver","path of geckodriver.exe");

def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    browser = webdriver.Firefox()
#    browser.minimize_window()

    #inp_name = given_name.replace(' ', '+').lower()
    if given_name != product_details['productUrl']:
        inp_name = urllib.parse.quote_plus(given_name)
        search_url = given_url + inp_name
    else:
        search_url = given_name

    browser.get(search_url)

     #sleep(10)
    data_list = []
    items = []
    #check for 404 error
    page_404_error = browser.find_elements_by_css_selector(".content-404>.h1")
    if len(page_404_error) > 0:
        is_unique_product_search = False
        if product_details['mpn'].strip() != "":
            if (product_details['mpn'].strip()).isnumeric():
                num = int(product_details['mpn'].strip())
                if num == 0:
                    name = product_details['product_scrap'].strip()
                else:
                    name = product_details['mpn'].strip()
            else:
                name = product_details['mpn'].strip()
        else:
            name = product_details['product_scrap']
        given_name = name
        browser.quit()
        data_list = scrap(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        #check for total number of results.
        try:
            search_results = browser.find_element_by_class_name("search-title").text.strip()
        except Exception as e:
            search_results = ""

        if search_results != "" and search_results.startswith("0"):
            print(search_results)
        else:
            if given_name != product_details['productUrl']:
                items = browser.find_elements_by_css_selector('.ais-hits--item.ais-hits--item')
                l.critical(f'{len(items)} Results Found for: {given_name}')
            else:
                items = browser.find_element_by_class_name('product-single')
                # title = items.find_elements_by_css_selector("h1[itemprop=\"name\"]")[0].text
                # price = items.find_elements_by_css_selector("span[class=\"price\"]")[0].text
                # sku = items.find_elements_by_css_selector("dd[data-sku]")[0].text
                try:
                    t1 = datetime.now()

                    try:
                        title = clean_text(items.find_elements_by_css_selector("h1[itemprop=\"name\"]")[0].text.strip())
                        # print(title)
                        url = product_details['productUrl'].strip()
                    except IndexError:
                        pass

                    try:
                        p = items.find_elements_by_css_selector("span[class=\"price\"]")[0].text
                        prd_price = clean_price(p)
                        if prd_price == '':
                            a = [][2]
                    except IndexError:
                        p = items.find_elements_by_css_selector("span[class=\"price\"]")[0].text
                        prd_price = clean_price(p)
                    except Exception as e:
                        print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(items.find_elements_by_css_selector('.merchant')[0].text)
                    except Exception as e:
                        n = e
                        # print(f'\n\n{e} marchant \n{title}\n\n')
                        merchant = 'Seller name not available'
                    try:
                        sku = clean_text(items.find_elements_by_css_selector("dd[data-sku]")[0].text)
                    except Exception as e:
                        sku = False

                    timestamp = datetime.now()
                    main = {
                        'name': title,
                        'price': prd_price,
                        'timestamp': timestamp,
                        'merchant': merchant,
                        'time': (datetime.now() - t1).total_seconds(),
                        'url': url,
                        'sku': sku,
                    }
                    data_list.append(main)
                except AttributeError:
                    pass
                browser.quit()
                return data_list

        if len(items) > 0 :
            for prd_data in items:
                try:
                    t1 = datetime.now()

                    try:
                        title = clean_text(
                            prd_data.find_elements_by_css_selector('.ais-hit--title.product-tile__title')[0].text)
                        # print(title)
                        url = prd_data.find_elements_by_css_selector('.product-tile')[0].get_attribute('href')
                    except IndexError:
                        continue

                    try:
                        p = prd_data.find_elements_by_css_selector('span.sale')[0].text
                        prd_price = clean_price(p)
                        if prd_price == '':
                            a = [][2]
                    except IndexError:
                        p = prd_data.find_elements_by_css_selector('span.ais-hit--price.price')[0].text
                        prd_price = clean_price(p)
                    except Exception as e:
                        print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(prd_data.find_elements_by_css_selector('.merchant')[0].text)
                    except Exception as e:
                        n = e
                        # print(f'\n\n{e} marchant \n{title}\n\n')
                        merchant = 'Seller name not available'

                    timestamp = datetime.now()
                    main = {
                        'name': title,
                        'price': prd_price,
                        'timestamp': timestamp,
                        'merchant': merchant,
                        'time': (datetime.now() - t1).total_seconds(),
                        'url': url,
                        'sku': False,
                    }
                    data_list.append(main)
                except AttributeError:
                    pass
                except Exception as e:
                    print(e, end=' AT GET DATA')
                    l.critical(e)
        else:
            print("No items found for scraping")
            if given_name == product_details['mpn'].strip():
                given_name = product_details['product_scrap'].strip()
                if given_name == "":
                    browser.quit()
                    return data_list
                data_list = scrap(given_name, given_url, given_model_no, is_unique_product_search, product_details)
                browser.quit()
                return data_list
        try:
            browser.quit()
        except Exception as e:
            n = e
            pass
    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
