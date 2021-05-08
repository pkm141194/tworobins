from selenium import webdriver
from datetime import datetime
from Functions import clean_text, clean_price
from selenium.webdriver.common.keys import Keys
from time import sleep


win_open = False


def scrap(given_name: str, given_url, given_model_no=None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    browser = webdriver.Firefox()
    # browser.minimize_window()
    browser.get(given_url)

    while True:
        try:
            input_field = browser.find_element_by_id('product-search-field')
            break
        except:
            input('Solve captcha and press enter 1:')

    input_field.clear()
    for char in given_name:
        input_field.send_keys(char)
        sleep(0.3)
    sleep(1)
    input_field.send_keys(Keys.RETURN)

    sleep(3)

    while True:
        try:
            items = browser.find_elements_by_css_selector('._1umis')
            break
        except:
            input('Solve captcha and press enter 2:')

    print(f'{len(items)} Results Found for: {given_name}')

    data_list = []
    for prd_data in items:
        try:
            t1 = datetime.now()

            try:
                while True:
                    try:
                        title = clean_text(prd_data.find_elements_by_css_selector('._1A_Xq')[0].text)
                        url = browser.find_element_by_css_selector('._1A_Xq>a').get_attribute('href')
                        break
                    except Exception as e:
                        print(e)
                        input('Solve captcha and press enter 3:')
                # print(title)
            except IndexError:
                continue

            try:
                print(prd_data.find_elements_by_css_selector('._2PrMB'))
                p = prd_data.find_elements_by_css_selector('._2PrMB')[0].text
                prd_price = clean_price(p)

            except IndexError:
                p = prd_data.find_elements_by_css_selector('._2PrMB')[0].text
                prd_price = clean_price(p)
            except Exception as e:
                n = e
                # print(f'\n{e} price\n{title}\n\n')
                prd_price = '0'

            try:
                merchant = clean_text(prd_data.find_elements_by_css_selector('.merchant')[0].text)
            except Exception as e:
                n = e
                # print(f'\n\n{e} marchant \n{title}\n\n')
                merchant = 'NA'

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
        except Exception as e:
            print(e, end=' AT GET DATA')
    try:
        browser.quit()
    except:
        print('Clear..')
    return data_list


def run(name, given_url, given_model_no=None):

    data = scrap(name, given_url, given_model_no)

    return data
