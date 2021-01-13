import random
import re
import time
import requests
from bs4 import BeautifulSoup

import database_manager
import parse_listings
from fake_useragent import UserAgent

user_agent = UserAgent().random

# class CookieParams:
#     def __init__(self):
#
#         self.uzma = None
#         self.uzmb = None
#         self.uzmc = None
#         self.uzmd = None
#         self.uzme = None
#         self.favorites_userid = None
#         self.y2_cohort_2020 = None
#         self.leadSaleRentFree = None
#
#         self.server_env = None
#         self.canary = None
#         self.abTestKey = None
#         self.y2018_2_cohort = 16
#         self.use_elastic_search = None
#
#     def add_attributes(self, **kwargs):
#         for key, value in kwargs.items():
#             if value is None:
#                 continue
#             else:
#                 setattr(self, key, value)
#
#         return self


def search(first_page_url):

    num_of_pages, cookie = get_number_of_pages(first_page_url)

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
        response = get_next_page(url, cookie)

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

    # cookie_object = CookieParams()
    # cookie_object.add_attributes(**cookie_dict)

    return cookies


def check_for_captcha(response):
    if "ShieldSquare Captcha" in response.text:
        input("Stuck on captcha. Press enter when done")
        return True
    else:
        return False


def get_cookie(response):

    cookie_params = response.headers['Set-Cookie']
    # print(cookie_params)
    cookies = update_cookie(cookie_params)

    return cookies


def get_next_page(url, cookies):

    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': user_agent,
        'DNT': '1',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': url,
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




