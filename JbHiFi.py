from selenium import webdriver
from datetime import datetime
from  time import sleep
from Functions import clean_text, clean_price


def scrap(given_name: str, given_url, given_model_no=None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    browser = webdriver.Firefox()
#    browser.minimize_window()

    inp_name = given_name.replace(' ', '+').lower()

    search_url = given_url + inp_name

    browser.get(search_url)

    sleep(10)

    items = browser.find_elements_by_css_selector('.ais-hits--item.ais-hits--item')

    print(f'{len(items)} Results Found for: {given_name}')

    data_list = []
    for prd_data in items:
        try:
            t1 = datetime.now()

            try:
                title = clean_text(prd_data.find_elements_by_css_selector('.ais-hit--title.product-tile__title')[0].text)
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
    try:
        browser.quit()
    except Exception as e:
        n = e
        pass
    return data_list


def run(name, given_url, given_model_no=None):

    data = scrap(name, given_url, given_model_no)

    return data
