import Amazon
import TheGoodGuys
import HarveyNorman
import Becex
import Catch
import MobileCiti
import Ebay
import JbHiFi
import OfficeWorks
import BingLee
import Kogan
import DickSmith
import sys

from Functions import get_data, post_data, Compare, calculate, find_model

url = {
    "https://www.amazon.com.au/":
        ("https://www.amazon.com.au/s?k=", 0.7, 1),

    "https://www.harveynorman.com.au/":
        ("https://www.harveynorman.com.au/catalogsearch/result/?q=", 0.90, 2),

    "https://www.thegoodguys.com.au/":
        ("https://www.thegoodguys.com.au/SearchDisplay?categoryId=&storeId=900"
         "&catalogId=30000&langId=-1&sType=SimpleSearch&resultCatEntryType=2"
         "&showResultsPage=true&searchSource=Q&pageView=&beginIndex=0&orderBy=0"
         "&pageSize=60&searchTerm= ", 0.5, 3),

    "https://www.becextech.com.au/":
        ("https://www.becextech.com.au/catalog/advanced_search_result.php?keywords=", 0.5, 4),

    "https://www.catch.com.au/":
        ("https://www.catch.com.au/search?query=", 0.8, 5),

    "https://www.mobileciti.com.au/":
        ("https://www.mobileciti.com.au/catalogsearch/result/?q=", 0.5, 6),

    "https://www.ebay.com.au/":
        ("https://www.ebay.com.au/sch/i.html?_nkw=", 0.8, 7),

    "https://www.jbhifi.com.au/":
        ("https://www.jbhifi.com.au/?query=", 0.8, 8),

    "https://www.officeworks.com.au/":
        ("https://www.officeworks.com.au/shop/officeworks/search?q={}&view=grid&page=1&sortBy=bestmatch", 0.7, 9),

    "https://www.binglee.com.au/":
        ("https://www.binglee.com.au/", 0.1, 10),

    "https://www.kogan.com/":
        ("https://www.kogan.com/", 0.1, 11),

    "https://www.dicksmith.com.au/da/":
        ("https://www.dicksmith.com.au/da/", 0.1, 12),
}

def scrap(given_name: str, given_url, given_model_no=None):
    try:
        selected = url[given_url]
      
    except Exception as e:
        sys.exit()
        
    url_id = selected[2]
    scrape_url = selected[0]
    get_filter_level = selected[1]
    scrape_data = []
#    print(name)
    print(f'Scraping data from {given_url}')
    if url_id == 1:
        if given_model_no is not None:
            scrape_data = Amazon.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = Amazon.run(given_name, scrape_url)

    if url_id == 2:
        if given_model_no is not None:
            scrape_data = HarveyNorman.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = HarveyNorman.run(given_name, scrape_url)

    if url_id == 3:
        if given_model_no is not None:
            scrape_data = TheGoodGuys.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = TheGoodGuys.run(given_name, scrape_url)

    if url_id == 4:
        if given_model_no is not None:
            scrape_data = Becex.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = Becex.run(given_name, scrape_url)

    if url_id == 5:
        if given_model_no is not None:
            scrape_data = Catch.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = Catch.run(given_name, scrape_url)

    if url_id == 6:
        if given_model_no is not None:
            scrape_data = MobileCiti.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = MobileCiti.run(given_name, scrape_url)

    if url_id == 7:
        if given_model_no is not None:
            scrape_data = Ebay.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = Ebay.run(given_name, scrape_url)

    if url_id == 8:
        if given_model_no is not None:
            scrape_data = JbHiFi.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = JbHiFi.run(given_name, scrape_url)

    if url_id == 9:
        if given_model_no is not None:
            scrape_data = OfficeWorks.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = OfficeWorks.run(given_name, scrape_url)

    if url_id == 10:
        if given_model_no is not None:
            scrape_data = BingLee.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = BingLee.run(given_name, scrape_url)

    if url_id == 11:
        if given_model_no is not None:
            scrape_data = Kogan.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = Kogan.run(given_name, scrape_url)

    if url_id == 12:
        if given_model_no is not None:
            scrape_data = DickSmith.run(given_name, scrape_url, given_model_no)
        else:
            scrape_data = DickSmith.run(given_name, scrape_url)

    return scrape_data, get_filter_level


if __name__ == '__main__':
    obj = Compare()
    while True:
        try:
            resp, name, price, seller, prd = get_data()
            if not resp:
                print("Data error..")
                continue
            model_found, model_no = find_model(name)
            abs_url = prd['url_scrap']
            if model_found:
                data, filter_level = scrap(name, abs_url, model_no)
            else:
                data, filter_level = scrap(name, abs_url)
            if len(data) < 1:
                print(f'No data matched for the query..')
                continue

            filtered_data, time = obj.filter(name, data, filter_level)
            if len(filtered_data) < 1:
                # For testing replace it with break
                continue
            min_price, comp, comp_price = calculate(filtered_data, price)
            post_data(filtered_data, min_price, comp, comp_price, time, abs_url, prd)

            # Comment the line below for api part
        #    break
        except Exception as e:
            print(f'\n\n\n\n{e}\n\n\n\n')
