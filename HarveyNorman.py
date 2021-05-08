from requests_html import HTMLSession
from datetime import datetime
from Functions import clean_text, clean_price


def get_links(given_name: str, given_url: str, given_model_no=None):
    session = HTMLSession()

    inp_name = given_name.replace(' ', '+').lower()

    search_url = given_url + inp_name

    r = session.get(url=search_url)

    items = r.html.find(".product-info-item.panel.panel_product.stock-in.cfx")

    print(f'{len(items)} Results Found for: {given_name}')

    f_link_list = []

    for item in items:
        try:
            links = item.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].text
            if given_model_no is not None:
                if given_model_no in links:
                    f_link_list.append(item)
        except AttributeError:
            print('Link not found \n')
            print(item.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].text)
        except Exception as e:
            print(e, end=" in GET LINKS\n\n")

    ret = f_link_list if given_model_no is not None else items
    return ret


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
    number = 1
    for link in links:
#        print(f'Getting data from link {number} of {len(links)}...')
        url = link.find('.name.fn.l_mgn-tb-sm.l_dsp-blc')[0].attrs['href']
        session = HTMLSession()
        r = session.get(url)

        number += 1
        try:
            t1 = datetime.now()

            try:
                title = clean_text(r.html.find('.product-name')[0].text)
                sku = r.html.find('.product-id.meta.quiet.p_txt-sm')[-1].text
            except IndexError:
                continue
            except Exception as e:
                n = e
                continue

            try:
                prd_price = clean_price(r.html.find('.price-device>script')[0].text)
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

    return data_list


def run(name, given_url, given_model_no=None):
    data = scrap(name, given_url, given_model_no)

    return data
