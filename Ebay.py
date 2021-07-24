from requests_html import HTMLSession
from datetime import datetime
import bs4
import time
from Functions import clean_text, clean_price
import logging
import urllib
import urllib3
import sys

urllib3.disable_warnings()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")


def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details=None):
    session = HTMLSession()

    # inp_name = given_name.replace(' ', '+').lower()

    # Murmu-0.1
    inp_name = urllib.parse.quote_plus(given_name)
    search_url = given_url + inp_name
    logging.debug(f'searching for the URL : {search_url}')

    r = session.get(url=search_url, verify=False)

    link_list = []
    f_link_list = []
    items = r.html.find(".s-item")
    #l.critical(f'{len(items)-1} Results Found for: {given_name}')
    product_search_count = r.html.find('h1.srp-controls__count-heading span.BOLD')[0].text
    product_search_result = product_search_count + " Results found for: " + r.html.find('span.BOLD')[1].text

    if int(product_search_count) > 0:
        l.critical(product_search_result)
        for item in items:
            try:
                links = item.find('.s-item__link')[0].absolute_links
                link = list(links)[0]
                link_list.append(link)
                if given_model_no is not None:
                    if given_model_no in item.find('.s-item__link')[0].text:
                        f_link_list.append(link)
            except AttributeError:
                print('Link not found \n')
                # print(item.find('.s-item__link')[0].text)
            except Exception as e:
                print(e, end=" in GET LINKS\n\n")
    else:
        l.critical(product_search_result)
        l.critical(product_search_result + "searching for " + product_details["product_scrap"].strip())
        print(product_search_result + "searching for " + product_details["product_scrap"].strip())
        is_unique_product_search = False
        if given_name != product_details["product_scrap"].strip():
            given_name = product_details["product_scrap"].strip()
            link_list = get_links(given_name, given_url, None, is_unique_product_search, product_details)
            f_link_list = link_list
    return f_link_list if given_model_no is not None else link_list


def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):
    """
    :param product_details:
    :param is_unique_product_search:
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    data_list = []
    data_found = True

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
            try:
                session = HTMLSession()
                prd_data = session.get(links[0], verify=False)
                msg = prd_data.html.find("p.error-header__headline")
                if prd_data.status_code != 200:
                    print('URL is invalid.')
                    data_found = False
                elif len(msg) > 0:
                    msg = msg[0].text.lower().strip()
                    #if msg == "We looked everywhere.".lower().strip():
                    print(f"No Results Found for {links[0]}")
                    logging.debug(f"No Results Found for {links[0]}")
                    data_found = False
            except:
                print('Error while getting data..\nRetrying in 2 seconds..')
                #time.sleep(2)
            if data_found:
                print(f"1 Results Found for {links[0]}")
                logging.debug(f"1 Results Found for {links[0]}")

                try:
                    title = clean_text(prd_data.html.find('#itemTitle')[0].text).replace('Details about ', '')
                except IndexError:
                    pass

                try:
                    sku = prd_data.html.find('#descItemNumber')[0].text
                except Exception as e:
                    exc = e
                    sku = ''

                try:
                    prd_price = clean_price(prd_data.html.find('#prcIsum')[0].text)              #prcIsum_bidPrice, prcIsum
                except Exception as e:
                    exc = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.html.find('span.mbg-nw')[0].text)
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    merchant = 'Seller name not available'

                try:
                    ratings_details = prd_data.html.find('div#si-fb')[0].text
                    merchant_ratings = ratings_details[:ratings_details.find('%') + 1]
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    merchant_ratings = 'merchant ratings not available'

                try:
                    product_mnp = getmpn(links[0])
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    product_mnp = 'NA'

                timestamp = datetime.now()
                main = {
                    'name': title,
                    'price': prd_price,
                    'timestamp': timestamp,
                    'merchant': merchant,
                    'merchant_ratings': merchant_ratings,
                    'time': (datetime.now() - t1).total_seconds(),
                    'url': links[0],
                    'sku': sku,
                    'mpn': product_mnp
                }
                print(f"product name is {main['name']}, price is {main['price']}, merchant is {main['merchant']}, merchant rating is {main['merchant_ratings']}, url is {main['url']}, sku is {main['sku']}, mpn is {main['mpn']}")
                logging.debug(main)
                data_list.append(main)
            else:
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
        for link in links:
            #        print(f'Getting data from link {n} of {len(links)}...')
            n += 1
            try:
                t1 = datetime.now()
                while True:
                    try:
                        session = HTMLSession()
                        prd_data = session.get(link, verify=False)
                        break
                    except:
                        print('Error while getting data..\nRetrying in 2 seconds..')
                        time.sleep(2)
                try:
                    title = clean_text(prd_data.html.find('#itemTitle')[0].text).replace('Details about ', '')
                except IndexError:
                    continue

                try:
                    sku = prd_data.html.find('#descItemNumber')[0].text
                except Exception as e:
                    exc = e
                    sku = ''

                try:
                    prd_price = clean_price(prd_data.html.find('#prcIsum')[0].text)
                except Exception as e:
                    exc = e
                    # print(f'\n{e} price\n{title}\n\n')
                    prd_price = '0'

                try:
                    merchant = clean_text(prd_data.html.find('span.mbg-nw')[0].text)
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    merchant = 'Seller name not available'

                try:
                    ratings_details = prd_data.html.find('div#si-fb')[0].text
                    merchant_ratings = ratings_details[:ratings_details.find('%') + 1]
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    merchant_ratings = 'merchant ratings not available'

                try:
                    product_mnp = getmpn(link)
                except Exception as e:
                    exc = e
                    # print(f'\n\n{e} marchant \n{title}\n\n')
                    product_mnp = 'merchant ratings not available'

                timestamp = datetime.now()
                main = {
                    'name': title,
                    'price': prd_price,
                    'timestamp': timestamp,
                    'merchant': merchant,
                    'merchant_ratings': merchant_ratings,
                    'time': (datetime.now() - t1).total_seconds(),
                    'url': link,
                    'sku': sku,
                    'mpn': product_mnp
                }
                data_list.append(main)
            except AttributeError:
                pass
    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):
    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data


def getmpn(url):
    mnp_str = ['Manufacturer Part Number:', 'MPN:']
    match_found = False
    session = HTMLSession()
    response = session.get(url, verify=False)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    tables = soup.select('div.itemAttr table')[0]
    rows = tables.findChildren(['tr'])
    for row in rows:
        cells = row.findChildren('td')
        for cell in cells:
            value = cell.string
            if match_found:
                next_str = cell.getText().strip()
                match_found = False
            if mnp_str[0] == cell.getText().strip() or mnp_str[1] == cell.getText().strip():
                match_found = True
    return next_str
