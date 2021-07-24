from requests_html import HTMLSession
from datetime import datetime
import sys
import logging
import urllib
import urllib3
import bs4

urllib3.disable_warnings()

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")
from Functions import clean_text, clean_price


def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details=None):
    session = HTMLSession()

    #inp_name = given_name.replace(' ', '+').lower()
    inp_name = urllib.parse.quote_plus(given_name)

    search_url = given_url + inp_name

    r = session.get(url=search_url, verify=False)

    items = r.html.find(".product-tile-inner.disp-block.clearfix")

    l.critical(f'{len(items)} Data Found for: {given_name}')

    f_link_list = []

    for item in items:
        try:
            links = item.find('.product-tile-name')[0].text
            if given_model_no is not None:
                if given_model_no in links:
                    f_link_list.append(item)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.product-tile-name')[0].text)
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
            data = [product_details["productUrl"]]
        else:
            data = get_links(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        if is_unique_product_search:
            data = [product_details["productUrl"]]
        else:
            data = get_links(given_name, given_url, None, is_unique_product_search, product_details)

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
        try:
            t1 = datetime.now()
            session = HTMLSession()
            prd_data = session.get(data[0], verify=False)
            if prd_data.status_code == 200:
                resp = bs4.BeautifulSoup(prd_data.text, 'lxml')
                try:
                    title = clean_text(resp.select('h1.pdp__main-title.text-light.text-graydark-3.text-center')[0].getText().strip())
                    url = resp.find_all(attrs={"rel": "canonical"})[0]['href']
                except IndexError:
                    pass

                try:
                    sku = resp.select('span.titleItems_model_digit.text-graylight-1')[0].getText()
                except Exception as e:
                    exc = e
                    sku = ''

                try:
                    #prd_price = clean_price(resp.select('span#offerPrice_3074457345620532168')[0].getText().strip().replace('$',''))
                    prd_price = clean_price(resp.select('.pricepoint-price')[0].text)
                except Exception as e:
                    exc = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.find('#sellerProfileTriggerId')[0].text)
                except Exception as e:
                    exc = e
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
                    'sku': sku,
                }
                data_list.append(main)
            else:
                print(prd_data.status_code)
                # check for unique code
                is_unique_product_search = False
                name = product_details["mpn"].strip()
                if name == "":
                    name = product_details["product_scrap"].strip()
                data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
        except AttributeError:
            pass
    else:
        n = 1
        for prd_data in data:
    #        print(f'Getting data from link {n} of {len(data)}...')
            n += 1
            try:
                t1 = datetime.now()

                try:
                    title = clean_text(prd_data.find('.product-tile-name')[0].text)
                    url = prd_data.find('a.disp-block')[0].attrs['href']
                except IndexError:
                    continue

                try:
                    sku = prd_data.find('.product-tile-model')[0].text
                except Exception as e:
                    exc = e
                    sku = ''

                try:
                    prd_price = clean_price(prd_data.find('.pricepoint-price')[0].text)
                except Exception as e:
                    exc = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.find('#sellerProfileTriggerId')[0].text)
                except Exception as e:
                    exc = e
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
                    'sku': sku,
                }
                data_list.append(main)
            except AttributeError:
                pass

    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
