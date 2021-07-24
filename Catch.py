from requests_html import HTMLSession
from datetime import datetime
from Functions import clean_text, clean_price
import logging
import bs4
import urllib
import urllib3
import sys

urllib3.disable_warnings()
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")


def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details = None):
    session = HTMLSession()

    #inp_name = given_name.replace(' ', '+').lower()


    inp_name = urllib.parse.quote_plus(given_name)
    #if is_unique_product_search:
    #    search_url = product_details['exact_product_name']
    #else:
    search_url = given_url + inp_name

    r = session.get(url=search_url, verify=False)

    items = r.html.find(".product")
    l.critical(f'{len(items)} Results Found for: {given_name}')

    #print(f'{len(items)} Results Found for: {given_name}')

    f_link_list = []

    for item in items:
        try:
            links = item.find('.product--title-link')[0].text
            if given_model_no is not None:
                if given_model_no in links:
                    f_link_list.append(item)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.product--title-link')[0].text)
        except Exception as e:
            print(e, end=" in GET LINKS\n\n")

    ret = f_link_list if given_model_no is not None else items
    return ret


def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    #given_model_no = None
    if given_model_no is not None:
        if is_unique_product_search:
            data = [product_details['productUrl']]
        else:
            data = get_links(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        if is_unique_product_search:
            data = [product_details['productUrl']]
        else:
            data = get_links(given_name, given_url, None, is_unique_product_search, product_details)
    data_list = []
    data_found = True
    if len(data) < 1:
        # check for unique code
        is_unique_product_search = False
        if given_name == product_details["mpn"].strip():
            name = product_details["product_scrap"].strip()
            data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
        else:
            return []
    elif len(data) == 1 and is_unique_product_search:
        logging.debug('you are in new block')
        try:
            t1 = datetime.now()
            session = HTMLSession()
            prd_data1 = session.get(url=data[0].strip(), verify=False)
            if prd_data1.status_code == 200:
                soup = bs4.BeautifulSoup(prd_data1.text, 'lxml')
                # Check if you found the result or not.
                try:
                    error_msg = soup.select('div.css-q8itik h1.css-1th4k77-h1.e12cshkt0')[0].getText()
                    data_found = False
                except Exception as e:
                    error_msg = ""
                    data_found = True

                if data_found:
                    #print(error_msg)
                    try:
                        title = clean_text(soup.select('h1.title')[0].getText())
                        url = data
                    except IndexError:
                        pass

                    try:
                        prd_price = clean_price(soup.select('span.price--dollars')[0].getText())
                    except Exception as e:
                        # print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(soup.select('.product-offer__seller-link')[0].getText().strip())
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
                else:
                    print(error_msg)
                    # check for unique code
                    is_unique_product_search = False
                    name = product_details["mpn"].strip()
                    if name == "":
                        name = product_details["product_scrap"].strip()
                    data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
            else:
                print(prd_data1.status_code)
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
                #session = HTMLSession()
                #prd_data1 = session.get(data, verify=False)
                try:
                    title = clean_text(prd_data.find('.product--title-link')[0].text)
                    url = list(prd_data.absolute_links)[1]
                except IndexError:
                    continue

                try:
                    prd_price = clean_price(prd_data.find('.price--dollars')[0].text)
                except Exception as e:
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.find('.product--seller')[0].text.strip())
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
            except AttributeError:
                pass

    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
