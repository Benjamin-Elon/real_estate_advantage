import random
import re
import time
import requests
from bs4 import BeautifulSoup
import playsound

import database_manager
import parse_listings
from fake_useragent import UserAgent

# I've discovered that using a set of two random user_agents results in so many fewer captchas.

user_agent = UserAgent().random
user_agent_1 = UserAgent().random


def search(first_page_url, max_pages):
    max_pages = int(max_pages)
    num_of_pages, cookies = get_number_of_pages(first_page_url)

    if max_pages < num_of_pages:
        num_of_pages = max_pages

    for page_num in range(2, num_of_pages+1):
        print("Fetching page:", page_num, '/', num_of_pages)
        params = first_page_url.split('realestate/rent?')[1]
        part_1 = 'https://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?'
        part_2 = '&compact-req=1&forceLdLoad=true'
        if page_num == 1:
            url = part_1 + params + part_2
        else:
            url = part_1 + params + '&page=' + str(page_num) + part_2
        # 'https://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?topArea=43&price=750-10000&squaremeter=0-300&compact-req=1&forceLdLoad=true'
        print(url)

        # get the next page
        if page_num == 2:
            url_1 = first_page_url + '&page=2'
            response = get_next_page(url, cookies, url_1)
        # response timeout
        if response.text is None:
            continue
        # parse the listings
        listing_list = parse_listings.parse_feedlist(response)
        listing_list = get_more_details(cookies, listing_list)
        database_manager.add_listings(listing_list)

        # Sleep for a bit between calls
        x = random.randrange(3, 7)
        print('sleeping for', x, 'seconds...')
        time.sleep(x)


def get_number_of_pages(url):

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
        'sec-gpc': '1',
    }

    response = requests.get(url, headers=headers)
    # print(response.text)
    soup = BeautifulSoup(''.join(response.text), 'html.parser')

    # no captcha
    if check_for_captcha(response) is False:
        cookies = get_cookie(response)

        if soup.find('button', {"class": "page-num"}) is None:
            total_pages = 1

        else:
            total_pages = int(soup.find('button', {"class": "page-num"}).contents[0].string)

    # captcha: re-fetch and refresh cookie
    else:
        total_pages, cookies = get_number_of_pages(url)

    return total_pages, cookies


def update_cookie(response):

    cookie_params = response.headers['Set-Cookie']
    # print(cookie_params)

    cookies = {}
    cookie_attributes = {'uzma': '__uzma=', 'uzmb': '__uzmb=', 'uzmc': '__uzmc=', 'uzmd': '__uzmd=', 'uzme': '__uzme',
                         'favorites_userid': 'favorites_userid=', 'y2_cohort_2020': 'y2_cohort_2020=',
                         'leadSaleRentFree': 'leadSaleRentFree=', 'canary': 'canary=', 'abTestKey': 'abTestKey=',
                         'server_env': 'server_env=', 'use_elastic_search': 'use_elastic_search='}

    # extract parameters from cookie
    for param, string in cookie_attributes.items():
        try:
            # find end index
            end = re.search(string, cookie_params).end()
            value = cookie_params[end:].split(';', 1)[0]
            # only add values present in the cookie
            if value is not None:
                cookies[param] = value
        except AttributeError:
            pass

    return cookies


def check_for_captcha(response):
    if "ShieldSquare Captcha" in response.text:
        print(response.url)
        playsound.playsound('ship_bell.mp3')
        input("Stuck on captcha. Press enter when done")
        x = input("replace user agent? (y/n)")
        if x == 'y':
            globals()['user_agent'] = UserAgent().random
        return True
    else:
        return False


def get_cookie(response):

    # print(cookie_params)
    cookies = update_cookie(response)

    return cookies


def get_next_page(url, cookies, url_1=None):
    if url_1 is None:
        url_1 = url
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': user_agent,
        'DNT': '1',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': url_1,
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
        'sec-gpc': '1',
    }
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'DNT': '1',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.yad2.co.il/realestate/rent?area=5&price=750-2000&squaremeter=40-80&page=2',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
        'sec-gpc': '1',
    }

    response = requests.get(url, headers=headers, cookies=cookies)

    # no captcha
    if check_for_captcha(response) is False:
        pass

    # captcha: re-fetch and refresh cookie
    else:
        response = get_next_page(url, cookies)

    return response


def get_more_details(cookies, listing_list):
    listing_list_1 = []
    # vary the ratio of opened to unopened by page. Some pages open a lot some pages fewer
    rand_1 = random.normalvariate(.9, .05)
    for listing in listing_list:

        result, listing_id = database_manager.check_extra_info(listing)
        if result is None:
            # leave some listings out to avoid ban
            rand = random.random()
            # print(rand, rand_1)
            if rand < rand_1:
                pass
            else:
                listing.scanned = 1
                listing_list_1.append(listing)
                continue

        # if a listing was previously scanned, but didn't get extra info: get info
        elif result['scanned'] == 1 and result['extra_info'] == 0:
            pass
        elif result['scanned'] == 1 and result['extra_info'] == 1:
            continue

        # time.sleep(rand)
        # print("getting extra_info:", listing_id)
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': user_agent,
            'DNT': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.yad2.co.il/realestate/rent?price=1000-1500&squaremeter=50-100',
            'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
            'sec-gpc': '1',
        }

        try:
            response = requests.get('https://www.yad2.co.il/api/item/' + listing.listing_id, headers=headers,
                                    cookies=cookies)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue

        cookies = update_cookie(response)
        extra_info = response.text
        if '504 Gateway Time-out' in extra_info or '502 Bad Gateway' in extra_info:
            print("Timed out other error")
            continue

        # no captcha
        if check_for_captcha(response) is False:

            listing = parse_listings.parse_extra_info(extra_info, listing)
            listing_list_1.append(listing)

        # captcha: re-fetch and refresh cookie
        else:
            continue

    return listing_list_1


def sql_to_dataframe():


# TODO add option to
def select_areas_to_scan():
    menu = []
    scope_names = ['Top_areas', 'Areas', 'Cities', 'Neighborhoods', 'Streets']
    df = sql_to_dataframe()
    area_ids = df[['area_id', 'area_name']].drop_duplicates()
    for area_id, area_name in area_ids.values:
        if area_name != '':
            menu.append([area_id, area_name])
        menu.sort(key=lambda tup: tup[1])

    for area_id, area_name in menu:
        print(area_name, '('+str(area_id)+')')

    print("Select desired areas:\n"
          "When finished, press enter.\n"
          "Press enter to search all areas.")

    area_ids = [x[0] for x in menu]
    x = None
    # Select as many areas as you want
    while True:
        x = input()
        if x == '' and area_ids == []:
            area_ids = area_ids
            break
        elif x == '':
            break
        try:
            x = int(x)
        except ValueError:
            print("invalid input")

        if x not in area_ids:
            print("invalid selection")
            continue
        elif x in area_ids:
            print("already selected")
            continue
        else:
            area_ids.append(x)

    urls = []
    for area_id in area_ids:
        url = 'https://www.yad2.co.il/realestate/rent?area=' + str(area_id) + '&price=1000-10000&squaremeter=0-300'
        urls.append(url)

    # give the urls a quick shuffle
    random.shuffle(urls)
    print(urls)

    return urls
