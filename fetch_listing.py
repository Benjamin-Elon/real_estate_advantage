import json
import random
import re
import time
import requests


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

def search():

    # It is pretty much impossible to switch listing page, even with a headless browser. Not sure hwo they did it.
    # To get around this, just search various price ranges, splitting up listings into smaller chunks
    price_list = [[0, 500], [500, 1000], [1000, 1200], [1200, 1300], [1300, 1400], [1400, 1500], [1500, 1550],
                  [1550, 1600],
                  [1600, 1650], [1650, 1700], [1700, 1750], [1750, 1800], [1800, 1850], [1850, 1900], [1900, 1950],
                  [1950, 2000], [2000, 2050], [2050, 2100], [2100, 2150], [2150, 2200], [2200, 2250], [2250, 2300],
                  [2300, 2350], [2350, 2400], [2400, 2450], [2450, 2500], [2500, 2600], [2600, 2700], [2700, 2800],
                  [2800, 2900], [2900, 3000], [3000, 3500], [3500, 4000], [4000, 4500], [4500, 5000],
                  [5000, 6000], [6000, 7000], [7000, 8000], [8000, 9000], [9000, 10000]]
    # random.shuffle(price_list)

    x = 0
    for price in price_list:
        url = "https://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?area=5&price=" \
              + str(price[0]) + "-" + str(price[1])
        print(url)
        if x == 0:
            cookie_object = get_first_cookie(url)
            response = get_page(url, cookie_object)
            x = 1
        else:
            response = get_page(url, cookie_object)
            cookie_params = response.headers['Set-Cookie']
            cookie_object = update_cookie(cookie_params)

        feedlist = response.text
        listing_ids = get_listing_ids(feedlist)
        print(listing_ids)

        x = random.randrange(7, 15)
        time.sleep(x)


def update_cookie(cookie_params):

    cookie_dict = {}

    end = re.search('__uzma=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    uzma = string[end:]
    cookie_dict['uzma'] = uzma

    end = re.search('__uzmb=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    uzmb = string[end:]
    cookie_dict['uzmb'] = uzmb

    end = re.search('__uzmc=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    uzmc = string[end:]
    cookie_dict['uzmc'] = uzmc

    end = re.search('__uzmd=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    uzmd = string[end:]
    cookie_dict['uzmd'] = uzmd

    end = re.search('__uzma=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    uzme = string[end:]
    cookie_dict['uzme'] = uzme

    end = re.search('favorites_userid=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    favorites_userid = string[end:]
    cookie_dict['favorites_userid'] = favorites_userid

    end = re.search('y2_cohort_2020=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    y2_cohort_2020 = string[end:]
    cookie_dict['y2_cohort_2020'] = y2_cohort_2020

    end = re.search('leadSaleRentFree=', cookie_params).end()
    string = cookie_params.split(';', 1)[0]
    leadSaleRentFree = string[end:]
    cookie_dict['leadSaleRentFree'] = leadSaleRentFree

    cookie_dict_1 = {}
    for key, value in cookie_dict.items():
        if value is not None:
            cookie_dict_1[key] = value

    cookie_object = CookieParams()
    cookie_object.add_attributes(**cookie_dict_1)
    return cookie_object


def get_first_cookie(url):

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
    if "ShieldSquare Captcha" in response.text:
        input("Stuck on captcha. Press enter when done")

    cookie_params = response.headers['Set-Cookie']

    cookie_object = update_cookie(cookie_params)

    return cookie_object


def get_page(url, cookie_object):

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

    if "ShieldSquare Captcha" in response.text:
        input("Stuck on captcha. Press enter when done")
        response = get_page(url, cookie_object)

    return response


def get_listing_ids(feedlist):

    response_dict = json.loads(feedlist)
    feed = response_dict["feed"]
    feed_items = feed["feed_items"]

    listing_list = []
    for listing in feed_items:
        listing = parse_listings.parse_listing(listing)
        listing_list.append(listing)



