import random
import re
import time
import requests
from bs4 import BeautifulSoup

import database_manager
import parse_listings


class CookieParams:
    def __init__(self):

        self.uzma = None
        self.uzmb = None
        self.uzmc = None
        self.uzmd = None
        self.uzme = None
        self.favorites_userid = None
        self.y2_cohort_2020 = None
        self.leadSaleRentFree = None

    def add_attributes(self, **kwargs):

        for key, value in kwargs.items():
            if value is None:
                continue
            else:
                setattr(self, key, value)

        return self


def search(first_page_url):

    num_of_pages, cookie_object = get_number_of_pages(first_page_url)

    for page_num in range(num_of_pages):
        params = first_page_url.split('realestate/rent?')[1]
        part_1 = 'https://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?'
        part_2 = '&compact-req=1&forceLdLoad=true'
        if page_num == 1:
            url = part_1 + params + part_2
        else:
            url = part_1 + params + '&page=' + str(page_num) + part_2

        print(url)

        # get the next page
        response = get_next_page(url, cookie_object)

        # parse the listings
        listing_list = parse_listings.parse_feedlist(response)
        database_manager.add_listings(listing_list)

        # Sleep for a bit between calls
        x = random.randrange(6, 13)
        time.sleep(x)


def get_number_of_pages(url):

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '^\\^Google',
        'sec-ch-ua-mobile': '?0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
    }

    response = requests.get(url, headers=headers)
    # print(response.text)
    soup = BeautifulSoup(''.join(response.text), 'html.parser')

    # no captcha
    if check_for_captcha(response) is False:
        cookie_object = get_cookie(response)

        if soup.find('button', {"class": "page-num"}) is None:
            total_pages = 1

        else:
            total_pages = int(soup.find('button', {"class": "page-num"}).contents[0].string)

    # captcha: re-fetch and refresh cookie
    else:
        total_pages, cookie_object = get_number_of_pages(url)

    return total_pages, cookie_object


def update_cookie(cookie_params):

    cookie_dict = {}
    cookie_attributes = ['__uzma=', '__uzmb=', '__uzmc=', '__uzmd=', '__uzma=', 'favorites_userid=', 'y2_cohort_2020=',
                         'leadSaleRentFree=']

    for attribute in cookie_attributes:
        try:
            end = re.search(attribute, cookie_params).end()
            string = cookie_params.split(';', 1)[0]
            value = string[end:]
            cookie_dict[attribute] = value
        except AttributeError:
            cookie_dict[attribute] = None

    cookie_dict_1 = {}
    for key, value in cookie_dict.items():
        if value is not None:
            cookie_dict_1[key] = value

    cookie_object = CookieParams()
    cookie_object.add_attributes(**cookie_dict_1)
    return cookie_object


def check_for_captcha(response):

    if "ShieldSquare Captcha" in response.text:
        input("Stuck on captcha. Press enter when done")
        return True
    else:
        return False


def get_cookie(response):

    cookie_params = response.headers['Set-Cookie']
    cookie_object = update_cookie(cookie_params)

    return cookie_object


def get_next_page(url, cookie_object):

    cookies = {
        '__uzma': cookie_object.uzma,
        '__uzmb': cookie_object.uzmb,
        '__uzme': cookie_object.uzme,
        'abTestKey': '75',
        'canary': 'never',
        'server_env': 'production',
        'y2018-2-cohort': '71',
        'leadSaleRentFree': cookie_object.leadSaleRentFree,
        'y2_cohort_2020': cookie_object.y2_cohort_2020,
        'use_elastic_search': '1',
        'favorites_userid': cookie_object.favorites_userid,
        '__uzmd': cookie_object.uzmd,
        '__uzmc': cookie_object.uzmc,
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '^\\^Google',
        'sec-ch-ua-mobile': '?0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
    }

    response = requests.get(url, headers=headers, cookies=cookies)

    # no captcha
    if check_for_captcha(response) is False:
        pass

    # captcha: re-fetch and refresh cookie
    else:
        response = get_next_page(url, cookie_object)

    return response




