import TheGoodGuys
import Amazon
import Catch
import MobileCiti
import Ebay
import HarveyNorman
import JbHiFi
import Becex
import sys
import logging
import urllib3
from Functions import get_data, post_data, Compare, calculate, find_model

urllib3.disable_warnings()

logging.basicConfig(filename='test.log',format='%(asctime)s %(message)s',filemode='a')

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")

# Add a file logger
f = logging.FileHandler("test.log")
l.addHandler(f)

# Add a stream logger
s = logging.StreamHandler()
l.addHandler(s)


url = {
"https://www.amazon.com.au/":
        ("https://www.amazon.com.au/s?k=", 0.5, 1),

    "https://www.harveynorman.com.au/":
        ("https://www.harveynorman.com.au/catalogsearch/result/?q=", 0.8, 2),

    "https://www.thegoodguys.com.au/":
        ("https://www.thegoodguys.com.au/SearchDisplay?categoryId=&storeId=900"
         "&catalogId=30000&langId=-1&sType=SimpleSearch&resultCatEntryType=2"
         "&showResultsPage=true&searchSource=Q&pageView=&beginIndex=0&orderBy=0"
         "&pageSize=60&searchTerm= ", 0.5, 3),

    "https://www.becextech.com.au/":
        ("https://www.becextech.com.au/catalog/advanced_search_result.php?keywords=", 0.5, 4),

    "https://www.catch.com.au/":
        ("https://www.catch.com.au/search?query=", 0.3, 5),

    "https://www.mobileciti.com.au/":
        ("https://www.mobileciti.com.au/catalogsearch/result/?q=", 0.5, 6),

    "https://www.ebay.com.au/":
        ("https://www.ebay.com.au/sch/i.html?_nkw=", 0.7, 7),

    "https://www.jbhifi.com.au/":
        ("https://www.jbhifi.com.au/?query=", 0.8, 8),

    "https://www.officeworks.com.au/":
        ("https://www.officeworks.com.au/shop/officeworks/search?q={}&view=grid&page=1&sortBy=bestmatch", 0.7, 9),

    "https://www.binglee.com.au/":
        ("https://www.binglee.com.au/", 0.5, 10),

    "https://www.kogan.com/au/":
        ("https://www.kogan.com/au/", 0.5, 11),

    "https://www.dicksmith.com.au/da/":
        ("https://www.dicksmith.com.au/da/", 0.5, 12),
}

def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):
    try:
        selected = url[given_url]
      
    except Exception as e:
        sys.exit()
        
    url_id = selected[2]
    scrape_url = selected[0]
    get_filter_level = selected[1]
    scrape_data = []
    l.critical(prd)
    l.critical(f'Scraping data from {given_url}')
    if url_id == 1:
        if given_model_no is not None:
            scrape_data = Amazon.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = Amazon.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 2:
        if given_model_no is not None:
            scrape_data = HarveyNorman.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = HarveyNorman.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 3:
        if given_model_no is not None:
            scrape_data = TheGoodGuys.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = TheGoodGuys.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 4:
        if given_model_no is not None:
            scrape_data = Becex.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = Becex.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 5:
        if given_model_no is not None:
            scrape_data = Catch.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = Catch.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 6:
        if given_model_no is not None:
            scrape_data = MobileCiti.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = MobileCiti.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 7:
        if given_model_no is not None:
            scrape_data = Ebay.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = Ebay.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    if url_id == 8:
        if given_model_no is not None:
            scrape_data = JbHiFi.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
        else:
            scrape_data = JbHiFi.run(given_name, scrape_url, is_unique_product_search, product_details)

    #if url_id == 9:
    #    if given_model_no is not None:
    #        scrape_data = OfficeWorks.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
    #    else:
    #        scrape_data = OfficeWorks.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    #if url_id == 10:
    #    if given_model_no is not None:
    #        scrape_data = BingLee.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
    #    else:
    #        scrape_data = BingLee.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    #if url_id == 11:
    #    if given_model_no is not None:
    #        scrape_data = Kogan.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
    #    else:
    #        scrape_data = Kogan.run(given_name, scrape_url, None, is_unique_product_search, product_details)

    #if url_id == 12:
    #    if given_model_no is not None:
    #        scrape_data = DickSmith.run(given_name, scrape_url, given_model_no, is_unique_product_search, product_details)
    #    else:
    #        scrape_data = DickSmith.run(given_name, scrape_url, None, is_unique_product_search, product_details)
    return scrape_data, get_filter_level


if __name__ == '__main__':
    obj = Compare()
    while True:
        try:
            resp, name, price, seller, prd, is_unique_product_search = get_data()
            if not resp:
                l.critical("Data error..")
                continue
            model_found, model_no = find_model(name)
            model_found=False
            abs_url = prd['url_scrap']
            if model_found:
                data, filter_level = scrap(name, abs_url, model_no, is_unique_product_search, prd)
            else:
                data, filter_level = scrap(name, abs_url, None, is_unique_product_search, prd)

            logging.debug(f'data  = {data} and filter_level = {filter_level}')
            if len(data) < 1:
                l.critical(f'No data matched for the query..')
                continue

            if name != data[0]['name']:
                name = data[0]['name']
                filtered_data, time = obj.filter(name, data, filter_level)
            if len(filtered_data) < 1:
                # For testing replace it with break
                continue
            min_price, comp, comp_price = calculate(filtered_data, price)
            post_data(filtered_data, min_price, comp, comp_price, time, abs_url, prd)

            # Comment the line below for api part
        #    break
        except Exception as e:
             l.critical(f'\n\n\n\n{e}\n\n\n\n')
