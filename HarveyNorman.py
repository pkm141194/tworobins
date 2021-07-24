from requests_html import HTMLSession
from datetime import datetime
from Functions import clean_text, clean_price
import sys
import logging
import urllib
import urllib3
import bs4

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")


def get_links(given_name: str, given_url: str, given_model_no=None, is_unique_product_search=False, product_details=None):
    session = HTMLSession()

    #inp_name = given_name.replace(' ', '+').lower()
    search_url = ""
    inp_name = urllib.parse.quote_plus(given_name)
    search_url = given_url + inp_name
    #search_url = query_url
    r = session.get(url=search_url, verify=False)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    search_text = soup.select("div#page h1")[0].getText()
    if search_text.startswith("0"):
        print(search_text)
        items = []
        ret = []
    else:
        #items = r.html.find(".product-info-item.panel.panel_product.stock-in.cfx")
        items = soup.select('div.product-item div.product-info-item.panel.panel_product.stock-in.cfx div.info a')
        l.critical(f'{len(items)} Results Found for: {given_name}')

        if len(items) > 0:
            f_link_list = []
            for item in items:
                try:
                    #links = item.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].text
                    links = item.getText()
                    if given_model_no is not None:
                        if given_model_no in links:
                            f_link_list.append(item)
                except AttributeError:
                    print('Link not found \n')
                    #print(item.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].text)
                    print(item.getText())
                except Exception as e:
                    print(e, end=" in GET LINKS\n\n")
        else:
            items = []
            f_link_list = []
    ret = f_link_list if given_model_no is not None else items
    return ret, soup


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
            links, soup = get_links(given_name, given_url, given_model_no, is_unique_product_search, product_details)
    else:
        if is_unique_product_search:
            links = [product_details["productUrl"]]
        else:
            links, soup = get_links(given_name, given_url, None, is_unique_product_search, product_details)
    data_list = []

    if len(links) < 1:
        # check for unique code
        is_unique_product_search = False
        if given_name == product_details["mpn"].strip() and product_details["mpn"].strip() != "":
            #You need to check the code here. If mpn result is empty it should go to scrape product.
            search_text = soup.select("div#page h1")[0].getText()
            if search_text.startswith("0"):
                name = product_details["product_scrap"].strip()
                if name != "":
                    data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
                else:
                    data_list = []
            else:
                try:
                    t1 = datetime.now()
                    session = HTMLSession()
                    inp_name = urllib.parse.quote_plus(given_name)
                    search_url = given_url + inp_name
                    r = session.get(url=search_url, verify=False)
                    soup = bs4.BeautifulSoup(r.text, 'lxml')
                    try:
                        # title = clean_text(r.html.find('.product-name')[0].text)
                        title = soup.select('span.product-name')[0].getText().strip()
                        # sku = r.html.find('.product-id.meta.quiet.p_txt-sm')[-1].text
                        sku = soup.select('div.col-xs-12.l_mgn-b-sm small.product-id.meta.quiet.p_txt-sm')[0].getText()
                    except IndexError:
                        title = ""
                        sku =""
                    except Exception as e:
                        # n = e
                        title = ""
                        sku = ""

                    try:
                        # prd_price = clean_price(r.html.find('.price-device>script')[0].text)
                        special_price = soup.select('div.special-price.pull-left span.price')
                        regular_price = soup.select('span.regular-price span.price')
                        if len(special_price) > 0:
                            prd_price = clean_price(special_price[0].getText().strip())
                        else:
                            prd_price = clean_price(regular_price[0].getText().strip())
                    except Exception as e:
                        n = e
                        # print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(soup.html.find('#sellerProfile')[0].text)
                    except Exception as e:
                        n = e
                        merchant = 'Seller name not available'

                    timestamp = datetime.now()
                    main = {
                        'name': title,
                        'price': prd_price,
                        'timestamp': timestamp,
                        'merchant': merchant,
                        'time': (datetime.now() - t1).total_seconds(),
                        'url': search_url,
                        'sku': sku,
                    }
                    data_list.append(main)
                except AttributeError:
                    pass
        else:
            name = product_details["product_scrap"].strip()
            data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    elif len(links) == 1 and is_unique_product_search:
        url = links[0]
        session = HTMLSession()
        r = session.get(url, verify=False)
        if r.status_code == 200:
            res = bs4.BeautifulSoup(r.text, 'lxml')
            search_text = res.select("div#page h1")[0].getText()
            if search_text.startswith("0"):
                print(search_text)
                data_list = []
                # check for unique code
                is_unique_product_search = False
                name = product_details["mpn"].strip()
                print("Retrying with mpn.")
                if name == "":
                    print("mpn is not available. Retrying with product_scrap value.")
                    name = product_details["product_scrap"].strip()
                if name != "":
                    data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
                else:
                    print("product_scrape is not available.")
                    data_list = []
            else:
                try:
                    t1 = datetime.now()

                    try:
                        # title = clean_text(r.html.find('.product-name')[0].text)
                        title = res.select('span.product-name')[0].getText().strip()
                        # sku = r.html.find('.product-id.meta.quiet.p_txt-sm')[-1].text
                        sku = res.select('div.col-xs-12.l_mgn-b-sm small.product-id.meta.quiet.p_txt-sm')[0].getText()
                    except IndexError:
                        pass
                    except Exception as e:
                        n = e
                        pass

                    try:
                        # prd_price = clean_price(r.html.find('.price-device>script')[0].text)
                        special_price = res.select('div.special-price.pull-left span.price')
                        regular_price = res.select('div.price-device.clearfix.l_mgn-tb-sm.price-device_lg span.regular-price span.price')
                        if len(special_price) > 0:
                            prd_price = clean_price(special_price[0].getText().strip())
                        else:
                            prd_price = clean_price(regular_price[0].getText().strip())
                    except Exception as e:
                        n = e
                        # print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(r.html.find('#sellerProfile')[0].text)
                    except Exception as e:
                        n = e
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
        else:
            print(f"{r.status_code} is returned for the {url}")
            # check for unique code
            is_unique_product_search = False
            name = product_details["mpn"].strip()
            print("Retrying with mpn.")
            if name == "":
                print("mpn is not available. Retrying with product_scrap value.")
                name = product_details["product_scrap"].strip()
            if name != "":
                data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)
            else:
                print("product_scrape is not available.")
                data_list = []
    else:
        number = 0
        for link in links:
    #        print(f'Getting data from link {number} of {len(links)}...')
            #url = link.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].attrs['href']
            if given_name == product_details["mpn"].strip():
                try:
                    t1 = datetime.now()
                    try:
                        # title = clean_text(r.html.find('.product-name')[0].text)
                        title = soup.select('span.product-name')[number].getText().strip()
                        # sku = r.html.find('.product-id.meta.quiet.p_txt-sm')[-1].text
                        sku = soup.select('div.col-xs-12.l_mgn-b-sm small.product-id.meta.quiet.p_txt-sm')[0].getText()
                    except IndexError:
                        continue
                    except Exception as e:
                        #n = e
                        continue

                    try:
                        # prd_price = clean_price(r.html.find('.price-device>script')[0].text)
                        special_price = soup.select('div.special-price.pull-left span.price')
                        regular_price = soup.select('div.price-device.clearfix.l_mgn-tb-sm.price-device_lg span.regular-price span.price')
                        if len(special_price) > 0:
                            prd_price = clean_price(special_price[number].getText().strip())
                        else:
                            prd_price = clean_price(regular_price[number].getText().strip())
                    except Exception as e:
                        n = e
                        # print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(r.html.find('#sellerProfile')[number].text)
                    except Exception as e:
                        n = e
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
                    number += 1
                except AttributeError:
                    pass
            else:
                url = link['href'].strip()
                session = HTMLSession()
                r = session.get(url, verify=False)
                if r.status_code == 200:
                    res = bs4.BeautifulSoup(r.text, 'lxml')
                    number += 1
                    try:
                        t1 = datetime.now()

                        try:
                            #title = clean_text(r.html.find('.product-name')[0].text)
                            title = res.select('span.product-name')[0].getText().strip()
                            #sku = r.html.find('.product-id.meta.quiet.p_txt-sm')[-1].text
                            sku = res.select('div.col-xs-12.l_mgn-b-sm small.product-id.meta.quiet.p_txt-sm')[0].getText()
                        except IndexError:
                            continue
                        except Exception as e:
                            n = e
                            continue

                        try:
                            #prd_price = clean_price(r.html.find('.price-device>script')[0].text)
                            special_price = res.select('div.special-price.pull-left span.price')
                            regular_price = res.select('span.regular-price span.price')
                            if len(special_price) > 0:
                                prd_price = clean_price(special_price[0].getText().strip())
                            else:
                                prd_price = clean_price(regular_price[0].getText().strip())
                        except Exception as e:
                            n = e
                            # print(f'\n{e} price\n{title}\n\n')
                            prd_price = '0'

                        try:
                            merchant = clean_text(r.html.find('#sellerProfile')[0].text)
                        except Exception as e:
                            n = e
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
                else:
                    print(r.status_code)
                    # check for unique code
                    #is_unique_product_search = False
                    #name = product_details["mpn"].strip()
                    #if name == "":
                    #    name = product_details["product_scrap"].strip()
                    #data_list = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details=None):
    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data
