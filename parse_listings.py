import json
import random

import requests
import soup_parser

from datetime import datetime
import re


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


def parse_listing(listing):
    listing_attributes = {}
    listing = {}
    listing_attributes['area_name'] = listing['AreaID_text'],
    listing_attributes['top_area_id'] = listing['topAreaID_text']
    listing_attributes['area_id'] = listing['area_id']
    listing_attributes['city_name'] = listing['city']
    listing_attributes['city_id'] = listing['city_code']
    listing_attributes['neighborhood'] = listing['neighborhood']
    listing_attributes['street'] = ['street']
    listing_attributes['building_number'] = listing['address_home_number']
    listing_attributes['price'] = listing['price']
    listing_attributes['date_added'] = listing['date_added']
    listing_attributes['entry_date'] = listing['date_of_entry']
    listing_attributes['updated_at'] = listing['updated_at']
    listing_attributes['customer_id'] = listing['customer_id']
    listing_attributes['contact_name'] = listing['contact_name']
    listing_attributes['listing_id'] = ['id']
    listing_attributes['cat_id'] = ['cat_id']
    listing_attributes['subcat_id'] = listing['subcat_id']
    listing_attributes['ad_number'] = listing['ad_number']
    listing_attributes['like_count'] = ['like_count']
    listing_attributes['latitude'] = listing['coordinates']['latitude']
    listing_attributes['longitude'] = listing['coordinates']['longitude']
    listing_attributes['rooms'] = listing['row_4'][0]['value']
    listing_attributes['floor'] = listing['row_4'][1]['value']
    listing_attributes['sqmt'] = listing['row_4'][2]['value']
    try:
        listing_attributes['realtor_name'] = listing['merchant_name']
    except KeyError:
        listing_attributes['realtor_name'] = None
    try:
        listing_attributes['description'] = listing['search_text']
        description = listing['search_text'].split('Floor_text $')[0].split('$FurnitureInfo')[1].split(
            listing_attributes['realtor_name'])
    except KeyError:
        listing_attributes['description'] = None

    # for item in description:
    # print(listing_attributes['description'])
    for key, value in listing_attributes.items():
        print(key, value)
        
    

