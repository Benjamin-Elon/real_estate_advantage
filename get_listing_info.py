import json
import random

import requests
import soup_parser

from datetime import datetime
import re

attrs_1 = ['"HouseCommittee":', '"TotalFloor_text":', '"ad_number":', '"asset_exclusive","value":',
           '"air_conditioner","value":', '"bars","value":', '"elevator","value":', '"accessibility","value":',
           '"renovated","value":', '"warhouse","value":', '"pets","value":',
           '"pandor_doors","value":', '"tadiran_c","value":', '"furniture","value":', '"long_term","value":',
           '"address_home_number":', '"address_more":', '"agency_contact_name":', '"ad","merchant":', '"customer_id":',
           '"agency_info_item_desc":', '"ad_number":', 'id":', '"price":', '"balconies":',
           'property_tax":', '"date_raw":', '"payments_in_year":', '"floor","title":', '"date_added":',
           '"city_text":', '"city_code":', '"rooms","title":', '"floor","title":']

attrs_2 = [['"rooms","title":"', '"titleWithoutLabel":', 'rooms'],
           ['"floor","title":', '"titleWithoutLabel":', 'floor'],
           ['"meter","title":', '"titleWithoutLabel":', 'sqmt']]

attrs_3 = ['"title":"ריהוט","popup_text":']

attribute_dict = {'"title":"ריהוט","popup_text":': 'furniture_desc',
                  '"HouseCommittee":': 'vaad_bayit',
                  '"TotalFloor_text":': 'building_floors',
                  '"asset_exclusive","value":': 'exclusive',
                  '"air_conditioner","value":': 'ac',
                  '"bars","value":': 'window_bars',
                  '"elevator","value":': 'elevator',
                  '"accessibility","value":': 'accessible',
                  '"renovated","value":': 'renovated',
                  '"warhouse","value":': 'storage_unit',
                  '"pets","value":': 'pets',
                  '"pandor_doors","value":': 'pandora_doors',
                  '"tadiran_c","value":': 'central_ac',
                  '"furniture","value":': 'furniture',
                  '"long_term","value":': 'long_term',
                  '"address_home_number":': 'building_number',
                  '"address_more":': 'address_desc',
                  '"agency_contact_name":': 'agency_contact_name',
                  '"ad","merchant":': 'realtor',
                  '"customer_id":': 'realtor_id',
                  '"agency_info_item_desc":': 'realtor_fee',
                  '"ad_number":': 'realtor_ad_id',
                  'id":': 'listing_id',
                  '"price":': 'price',
                  '"info_text":': 'description',
                  '"balconies":': 'balconies',
                  'property_tax":': 'arnona',
                  '"date_raw":': 'entry_date',
                  '"payments_in_year":': 'yearly_payments',
                  '"floor","title":': 'floor_name_heb',
                  '"date_added":': 'original_post_date',
                  '"city_text":': 'city',
                  '"city_code":': 'city_id',
                  '"contact_name":': 'contact_name',
                  '"rooms","title":': "rooms_name_heb", }


class ListingConstructor:

    def __init__(self):

        self.listing_url = None
        self.url = None
        self.date_posted = None
        self.apt_type = None
        self.neighborhood = None
        self.city = None
        self.street = None
        self.building_number = None
        self.floor = None
        self.floor_name_heb = None
        self.sqmt = None
        self.rooms = None
        self.image = None
        self.price = None
        self.realtor = None
        self.num_on_page = None
        self.listing_id = None
        self.original_post_date = None
        self.entry_date = None
        self.listing_age = None
        self.age = None
        self.vaad_bayit = None
        self.balconies = None
        self.building_floors = None
        self.num_payments = None
        self.arnona = None
        self.parking_spots = None
        self.elevator = None
        self.roommates = None
        self.b_shelter = None
        self.pandora_doors = None
        self.ac = None
        self.central_ac = None
        self.accessible = None
        self.window_bars = None
        self.furniture = None
        self.kosher_kitchen = None
        self.pets = None
        self.storage_unit = None
        self.renovated = None
        self.long_term = None
        self.entrance_num = None
        self.description = None
        self.extra = None
        self.listing_rank = None
        self.platinum = None
        self.confidence = 1
        self.address_desc = None
        self.agency_contact_name = None
        self.realtor_id = None
        self.realtor_fee = None
        self.realtor_ad_id = None
        self.yearly_payments = None
        self.contact_name = None
        self.rooms_name_heb = None

        self.city_id = None
        self.neighborhood_id = None
        self.street_id = None
        self.search_url_id = None

    def add_attributes(self, **kwargs):

        for key, value in kwargs.items():
            if value is None:
                continue
            else:
                setattr(self, key, value)

        return self


def convert_values(value):
    try:
        value = float(value)
    # Not a number
    except ValueError:
        try:
            value = datetime.strftime(value, '%Y-%m-%d')
        except TypeError:
            value = value.replace('₪', '').strip()
            try:
                value = float(value)
            except ValueError:
                return value

    return value


def parse_listing_response(content):
    """don't even know how they did the formatting here.
    It's virtually impossible to turn into a dictionary. The syntax is just...off. """

    listing_list = []

    attr_dict = {}
    listing = ListingConstructor()
    listing_list.append(listing)
    fail = []

    for item in attrs_1:
        # print(item)
        attribute_name = attribute_dict[item]
        try:
            index_end = re.search(item, content).end()
            # print(index_end)
            value = content[index_end:].split(',', 1)[0]
            # print(value)
            attr_dict[attribute_name] = value
            print(attribute_name, ": ", value)
        except AttributeError:
            fail.append(attribute_name)

    for string_1, string_2, attribute_name in attrs_2:
        try:
            text = content[re.search(string_1, content).end():].split('}', 1)[0]
            value = text[re.search(string_2, text).end():]
            attr_dict[attribute_name] = value
            print(attribute_name, ": ", value)
        except AttributeError:
            fail.append(attribute_name)

    for item in attrs_3:
        attribute_name = attribute_dict[item]
        try:
            value = content[re.search(item, content).end():].split('}', 1)[0]
            attr_dict[attribute_name] = value
        except AttributeError:
            fail.append(attribute_name)

    for item in fail:
        print("FAIL:", item)
    listing.add_attributes(**attr_dict)

    return listing


def get_listings_info(id_list):
    listing_urls = []
    for listing_id in id_list:
        x = random.randrange(0, 2)
        if x == 0:
            url = 'https://www.yad2.co.il/item/' + listing_id
        else:
            url = 'http://www.yad2.co.il/item/' + listing_id
        listing_urls.append(url)

    for url in listing_urls:
        while True:
            headers = get_request_headers(url)
            response = requests.get(url, headers=headers)
            content = response.text.replace('false', "False").replace("true", "True").replace(r"\/", "")
            content = content.encode('utf-8').decode('unicode-escape')
            print(content)
            if "ShieldSquare Captcha" in content:
                input("Stuck on captcha. Press enter when done")
                continue
            else:
                break

        listing_list = []
        listing = parse_listing_response(content)
        listing_list.append(listing)


def get_request_headers(url):

    # user_agents = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01',
    #                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    #                '54.0.2840.71 Safari/537.36',
    #                'Mozilla/5.0 (Linux; Ubuntu 14.04) AppleWebKit/537.36 Chromium/35.0.1870.2 Safa'
    #                'ri/537.36',
    #                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.'
    #                '0.2228.0 Safari/537.36',
    #                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko'
    #                ') Chrome/42.0.2311.135 '
    #                'Safari/537.36 Edge/12.246',
    #                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, '
    #                'like Gecko) Version/9.0.2 Safari/601.3.9',
    #                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                'Chrome/47.0.2526.111 Safari/537.36',
    #                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0']
    #
    # x = random.randrange(0, len(user_agents))
    # user_agent = user_agents[x]

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '^\\^Google',
        'sec-ch-ua-mobile': '?0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
    }


    return headers

# def scan_url(url):
#     pages_to_fetch = 1
#     page_number = 1
#
#     first_page_url = url
#
#     # url_date = fetch_from_db.get_url_date(first_page_url, todays_date)
#     print("Fetching search_url.")
#     soup = fetch_listings(url)
#
#     # Loop through pages up to page chosen
#     while page_number <= pages_to_fetch:
#
#         print("Processing page:", page_number, "\n")
#         # Get number of pages while fetching first page
#         if page_number == 1:
#
#             total_pages = soup_parser.get_num_pages(soup)
#             if total_pages is None:
#                 print("No results: ", url)
#                 return
#             elif total_pages == 1:
#                 print("One page of results.\nProcessing...")
#             else:
#                 print("There are ", total_pages, " pages of results.")
#                 pages_to_fetch = int(input("Enter the number of pages to fetch:\n"))

# else:
#     '''
#     Site now breaks if you try to navigate using url instead of site buttons
#     '''
#     # get search_url for next page
#     url = listing_parser.next_page_url(url, page_number)
#     # soup = get_soup.fetch_page(driver, url)[0]
#     soup = get_soup.navigate_to_next(page_number, total_pages, driver)
