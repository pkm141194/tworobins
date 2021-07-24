from requests_html import HTMLSession
from datetime import datetime
from Functions import clean_text, clean_price
import bs4
import urllib
import urllib3

import sys
import logging

urllib3.disable_warnings()
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")
def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details = None):
    session = HTMLSession()

    #inp_name = given_name.replace(' ', '+').lower()
    inp_name = urllib.parse.quote_plus(given_name)

    search_url = given_url + inp_name

    r = session.get(url=search_url, verify=False)
    soup = bs4.BeautifulSoup(r.text, 'lxml')

    items = r.html.find(".pro-box")

    l.critical(f'{len(items)} Results Found for: {given_name}')

    f_link_list = []

    for item in items:
        try:
            links = item.find('.pro-txt')[0].find('a')[0].text
            if given_model_no is not None:
                if given_model_no in links:
                    f_link_list.append(item)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.pro-txt')[0].find('a')[0].text)
        except Exception as e:
            print(e, end=" in GET LINKS\n\n")

    ret = f_link_list if given_model_no is not None else items
    return ret, soup


def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    if given_model_no is not None:
        if is_unique_product_search:
            data = [product_details['productUrl']]
        else:
            data, soup = get_links(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        if is_unique_product_search:
            data = [product_details['productUrl']]
        else:
            data, soup = get_links(given_name, given_url, None, is_unique_product_search, product_details)


    data_list = []

    if len(data) < 1:
        # check for unique code
        is_unique_product_search = False
        if given_name == product_details["mpn"].strip():
            name = product_details["product_scrap"].strip()
            data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
        else:
            return []
    elif len(data) == 1 and is_unique_product_search:
        session = HTMLSession()
        r = session.get(url=data[0].strip(), verify=False)
        if r.status_code == 200:
            soup = bs4.BeautifulSoup(r.text, 'lxml')
            #no_product = []
            try:
                no_product = soup.select('table.productListing div.no_product')
            except Exception as e:
                no_product = []
            #print(no_product)
            if len(no_product) > 0:
                print(no_product[0].getText())
                is_unique_product_search = False
                name = product_details["product_scrap"].strip()
                if name != "":
                    data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
                else:
                    data_list = []
            else:
                try:
                    t1 = datetime.now()

                    try:
                        # title = clean_text(prd_data.find('.pro-txt')[0].find('a')[0].text)
                        title = clean_text(soup.select('div.det-hd')[0].getText().strip())
                        # url = list(prd_data.absolute_links)[1]
                        url = soup.find_all(attrs={"itemprop": "url"})[0]['content']
                    except IndexError:
                        pass

                    try:
                        prd_price = clean_price(soup.find_all(attrs={"itemprop": "price"})[0].getText().replace(',',''))
                    except Exception as e:
                        # print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(soup.find('.merchant')[0].text)
                    except Exception as e:
                        # print(f'\n\n{e} marchant \n{title}\n\n')
                        merchant = 'Seller name not available'

                    timestamp = datetime.now()
                    main = {
                        'name': title,
                        'price': prd_price,
                        'timestamp': timestamp,
                        'merchant': merchant,
                        'time': (datetime.now() - t1).total_seconds(),
                        'url': url
                    }
                    data_list.append(main)
                    #n += 1
                except AttributeError:
                    pass
        else:
            #check  product scrape.
            print(r.status_code)
            # check for unique code
            is_unique_product_search = False
            #name = product_details["mpn"].strip()
            #if name == "":
            name = product_details["product_scrap"].strip()
            if name != "":
                data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
            else:
                data_list = []
    else:
        n = 0
        for prd_data in data:
    #        print(f'Getting data from link {n} of {len(data)}...')

            try:
                t1 = datetime.now()

                try:
                    #title = clean_text(prd_data.find('.pro-txt')[0].find('a')[0].text)
                    title = clean_text(soup.select('div.pro-img')[n].select('img')[0]['alt'])
                    #url = list(prd_data.absolute_links)[1]
                    url = soup.select('div.pro-img')[n].select('a')[0]['href']
                except IndexError:
                    continue

                try:
                    prd_price = clean_price(soup.select('div.pro-box')[n].select('span.productSpecialPrice')[0].getText())
                except Exception as e:
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.find('.merchant')[n].text)
                except Exception as e:
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    merchant = 'Seller name not available'

                timestamp = datetime.now()
                main = {
                    'name': title,
                    'price': prd_price,
                    'timestamp': timestamp,
                    'merchant': merchant,
                    'time': (datetime.now() - t1).total_seconds(),
                    'url': url
                }
                data_list.append(main)
                n += 1
            except AttributeError:
                pass

    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
