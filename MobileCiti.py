from requests_html import HTMLSession
from datetime import datetime
from Functions import clean_text, clean_price
import sys
import logging
import urllib
import urllib3
import bs4

urllib3.disable_warnings()

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")


def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details=None):
    session = HTMLSession()

    #inp_name = given_name.replace(' ', '+').lower()
    inp_name = urllib.parse.quote_plus(given_name)
    search_url = given_url + inp_name

    r = session.get(url=search_url)

    items = r.html.find(".item.product.product-item")

    l.critical(f'{len(items)} Results Found for: {given_name}')

    f_link_list = []

    for item in items:
        try:
            links = item.find('.product-item-link')[0].text
            if given_model_no is not None:
                if given_model_no in links:
                    f_link_list.append(item)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.product-item-link')[0].text)
        except Exception as e:
            print(e, end=" in GET LINKS\n\n")

    ret = f_link_list if given_model_no is not None else items
    return ret


def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    if given_model_no is not None:
        if is_unique_product_search:
            links = [product_details["productUrl"]]
        else:
            links = get_links(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        if is_unique_product_search:
            links = [product_details["productUrl"]]
        else:
            links = get_links(given_name, given_url, None, is_unique_product_search, product_details)
    data_list = []

    if len(links) < 1:
        # check for unique code
        is_unique_product_search = False
        if given_name == product_details["mpn"].strip():
            name = product_details["product_scrap"].strip()
            data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
        else:
            return []
    elif len(links) == 1 and is_unique_product_search:
        try:
            t1 = datetime.now()
            session = HTMLSession()
            req = session.get(url=links[0].strip(), verify=False)
            if req.status_code == 200:
                res = bs4.BeautifulSoup(req.text, 'lxml')
                try:
                    title = clean_text(res.select('h1.page-title span.base')[0].getText())
                except IndexError:
                    pass

                try:
                    sku = res.select("div.product-info-main p strong")[0].getText()
                except Exception as e:
                    print(e)
                    sku = ''

                try:
                    #res.find_all(attrs={"data-price-type": "finalPrice"})[0].getText()
                    prd_price = clean_price(res.select('span.price-container.price-final_price.tax.weee.rewards_earn span.price')[1].getText())
                except Exception as e:
                    n = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(res.html.find('.product--seller')[0].text)
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
                    'url': links[0],
                    'sku': sku
                }
                data_list.append(main)
            else:
                print(req.status_code)
                # check for unique code
                is_unique_product_search = False
                name = product_details["mpn"].strip()
                if name == "":
                    name = product_details["product_scrap"].strip()
                data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
        except AttributeError:
            pass
    else:
        number = 1
        for link in links:
            url = link.find('.product-item-link')[0].attrs['href']
            session = HTMLSession()
            r = session.get(url, verify=False)
            number += 1

            try:
                t1 = datetime.now()

                try:
                    title = clean_text(r.html.find('.page-title')[0].text)
                except IndexError:
                    continue

                try:
                    sku = r.html.find('.product-info-main>p>strong')[0].text
                except Exception as e:
                    print(e)
                    sku = ''

                try:
                    prd_price = clean_price(r.html.find('.price')[0].text)
                except Exception as e:
                    n = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(r.html.find('.product--seller')[0].text)
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
                    'sku': sku
                }
                data_list.append(main)
            except AttributeError:
                pass

    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
