from requests_html import HTMLSession
from datetime import datetime
import time
from Functions import clean_text, clean_price


def get_links(given_name: str, given_url: str, given_model_no=None):
    session = HTMLSession()

    inp_name = given_name.replace(' ', '+').lower()

    search_url = given_url + inp_name

    r = session.get(url=search_url)

    items = r.html.find(".sg-col-4-of-12.s-result-item.s-asin.sg-col-4-of-16.sg-col.sg-col-4-of-20")

    print(f'{len(items)} Results Found for: {given_name}')

    link_list = []
    f_link_list = []

    for item in items:
        try:
            links = item.find('.a-link-normal.a-text-normal')[0].absolute_links
            link = list(links)[0]
            link_list.append(link)
            if given_model_no is not None:
                if given_model_no in item.find('.a-link-normal.a-text-normal')[0].text:
                    f_link_list.append(link)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.a-link-normal.a-text-normal')[0].text)
        except Exception as e:
            print(e, end=" in GET LINKS\n\n")

    return f_link_list if given_model_no is not None else link_list


def scrap(given_name: str, given_url, given_model_no=None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    if given_model_no is not None:
        links = get_links(given_name, given_url, given_model_no)
    else:
        links = get_links(given_name, given_url)

    if len(links) < 1:
        return []

    data_list = []
    n = 1
    for link in links:
#        print(f'Getting data from link {n} of {len(links)}...')
        n += 1
        try:
            t1 = datetime.now()
            while True:
                try:
                    session = HTMLSession()
                    prd_data = session.get(link)
                    break
                except:
                    print('Error while getting data..\nRetrying in 2 seconds..')
                    time.sleep(2)
            try:
                title = clean_text(prd_data.html.find('#productTitle')[0].text)
            except IndexError:
                continue

            try:
                table = prd_data.html.find('tr')
                sku = ''
                for row in table:
                    try:
                        th = row.text
                        if 'model' in th.lower() and 'number' in th.lower():
                            sku = row.find('td')[0].text
                            break
                    except IndexError:
                        continue
            except Exception as e:
                exc = e
                sku = ''

            try:
                prd_price = clean_price(prd_data.html.find('#price_inside_buybox')[0].text)
            except Exception as e:
                exc = e
                # print(f'\n{e} price\n{title}\n\n')
                prd_price = '0'

            try:
                merchant = clean_text(prd_data.html.find('#sellerProfileTriggerId')[0].text)
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
                'url': link,
                'sku': sku,
            }
            data_list.append(main)
        except AttributeError:
            print('Error 0005')

    return data_list


def run(name, given_url, given_model_no=None):

    data = scrap(name, given_url, given_model_no)

    return data
