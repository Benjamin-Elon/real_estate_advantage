# -*- coding: utf-8 -*-
import codecs
import json
import re
from datetime import datetime


class ListingConstructor:
    """A class meant to represent an individual apartment listing"""
    def __init__(self):

        self.top_area_name = None
        self.top_area_id = None
        self.area_name = None
        self.area_id = None
        self.city_name = None
        self.city_id = None
        self.neighborhood_name = None
        self.neighborhood_id = None
        self.street_name = None
        self.street_id = None
        self.building_number = None
        self.price = None
        self.date_added = None
        self.entry_date = None
        self.updated_at = None
        self.customer_id = None
        self.contact_name = None
        self.listing_id = None
        self.category_id = None
        self.subcategory_id = None
        self.ad_number = None
        self.realtor_name = None
        self.apt_type = None
        self.apartment_state = None
        self.balconies = None
        self.sqmt = None
        self.rooms = None
        self.latitude = None
        self.longitude = None
        self.floor = None
        self.ac = None
        self.b_shelter = None
        self.furniture = None
        self.central_ac = None
        self.sunroom = None
        self.storage = None
        self.accesible = None
        self.parking = None
        self.pets = None
        self.window_bars = None
        self.elevator = None
        self.central_ac = None
        self.sub_apartment = None
        self.renovated = None
        self.long_term = None
        self.pandora_doors = None
        self.roommates = None
        self.vaad_bayit = None
        self.building_floors = None
        self.arnona = None
        self.furniture_description = None
        self.description = None
        self.realtor = None
        self.extra_info = 0
        self.confidence = 1

    def add_attributes(self, **kwargs):

        for key, value in kwargs.items():
            if value is None:
                continue
            else:
                convert_values(value)
                setattr(self, key, value)

        return self

    def compare_listing(self, comparison_listing, parameters):
        """compares changes between a listing to a possible matching listing"""
        self_attrs_dict = dict()
        comp_attrs_dict = dict()
        changes = dict()

        # attrs that aren't relevant to comparison when comparing all attributes
        ignore_attrs = ("image", "num_on_page", "url", "listing_id", "listing_url", "listing_rank", "confidence")

        if parameters == "all":
            self_attrs_dict = self.__dict__
            comp_attrs_dict = comparison_listing.__dict__
            for key in self_attrs_dict.keys():
                if key in ignore_attrs:
                    del self_attrs_dict[key]

        else:
            for attr in parameters:
                self_attrs_dict[attr] = getattr(self, attr)
                comp_attrs_dict[attr] = getattr(self, attr)

        for key, new_value in self_attrs_dict.items():
            if comp_attrs_dict[key] != new_value:
                new_old = {"new": new_value, "old": comp_attrs_dict[key]}
                changes[key] = new_old

        return changes


def convert_values(value):
    """Converts listing parameters to their appropriate types"""
    # if isinstance(value, list):
    #     separator = ', '
    #     value = separator.join(value)
    try:
        value = float(value)
    # Not a number
    except ValueError:
        try:
            value = datetime.strftime(value, '%Y-%m-%d')
        except TypeError:
            try:
                value = float(value)
            except ValueError:
                return value

    return value


def clean_attributes(listing_attributes):
    """
    cleans listing parameters so they can be properly processed
    Returns: listing_attributes
    """
    # print(listing_attributes)
    price = listing_attributes['price'].replace('₪', '').replace(',', '').strip()
    if isinstance(price, str):
        try:
            price = int(price)
        except (TypeError, ValueError):
            price = None
    listing_attributes['price'] = price

    if listing_attributes['date_added'] is not None:
        listing_attributes['date_added'] = listing_attributes['date_added'][0:10]

    if listing_attributes['entry_date'] is not None:
        listing_attributes['entry_date'] = listing_attributes['entry_date'][0:10]

    if listing_attributes['updated_at'] == 'עודכן היום':
        listing_attributes['updated_at'] = datetime.today().date().strftime('%Y-%m-%d')
    else:
        listing_attributes['updated_at'] = datetime.strftime(
            datetime.strptime(listing_attributes['updated_at'].replace('עודכן ב', '').strip(), '%d/%m/%Y'), '%Y-%m-%d')

    if listing_attributes['floor'] == 'קרקע':
        listing_attributes['floor'] = 0

    return listing_attributes


def parse_feedlist(response):
    """
    Extracts listings from site response
    Returns: listing_list
    """
    listing_list = []

    response = response.text
    try:
        response_dict = json.loads(response)
    except json.decoder.JSONDecodeError:
        return listing_list
    feed = response_dict["feed"]
    feedlist = feed["feed_items"]
    # for item in feedlist:
    #     print(item, '\n')

    listing_items = [['top_area_name', 'topAreaID_text'], ['area_name', 'AreaID_text'], ['area_id', 'area_id'],
                     ['city_id', 'city_code'], ['city_name', 'city'], ['neighborhood_name', 'neighborhood'],
                     ['street_name', 'street'],
                     ['building_number', 'address_home_number'], ['price', 'price'], ['date_added', 'date_added'],
                     ['entry_date', 'date_of_entry'], ['updated_at', 'updated_at'], ['customer_id', 'customer_id'],
                     ['contact_name', 'contact_name'], ['listing_id', 'id'], ['category_id', 'cat_id'],
                     ['subcategory_id', 'subcat_id'], ['ad_number', 'ad_number'],
                     ['realtor_name', 'merchant_name'], ['apt_type', 'HomeTypeID_text'],
                     ['apartment_state', 'AssetClassificationID_text'], ['sqmt', 'square_meters'],
                     ['rooms', 'Rooms_text']]

    bool_attributes = [['AirConditioner_text', 'ac'], ['mamad_text', 'b_shelter'], ['Furniture_text', 'furniture'],
                       ['Tadiran_text', 'central_ac'], ['sunpatio_text', 'sunroom'], ['storeroom_text', 'storage'],
                       ['handicapped_text', 'accesible'], ['Parking_text', 'parking'], ['PetsInHouse_text', 'pets'],
                       ['Grating_text', 'window_bars'], ['Elevator_text', 'elevator'],
                       ['yehidatdiur_text', 'sub_apartment'], ['Meshupatz_text', 'renovated'],
                       ['LongTerm_text', 'long_term'], ['PandorDoors_text', 'pandora_doors'],
                       ['patio_text', 'balconies'], ['Partner_text', 'roommates']]

    x = 0

    for listing in feedlist:
        # print(listing)
        # remove irrelevant keys
        if listing.get('type') != 'ad':
            continue
        elif listing.get('title') == 'דירות להשכרה מתיווך':
            continue
        elif listing.get('text') == 'לא נמצאו תוצאות':
            continue

        print("Listing:", x, "Id:", listing['id'])
        x += 1

        listing_attributes = {}

        # parse out all the listings attributes
        for attribute_name, key in listing_items:
            try:
                listing_attributes[attribute_name] = listing[key]
            except KeyError:
                listing_attributes[attribute_name] = None
                print("ERROR:", attribute_name)
        try:
            listing_attributes['latitude'] = listing['coordinates']['latitude']
        except KeyError:
            print("FAIL: latitude")
        try:
            listing_attributes['longitude'] = listing['coordinates']['longitude']
        except KeyError:
            print("FAIL: longitude")

        try:
            listing_attributes['floor'] = listing['row_4'][1]['value']
        except KeyError:
            print("FAIL: floor")

        for key, attribute_name in bool_attributes:
            try:
                if listing[key] == '':
                    listing_attributes[attribute_name] = 0
                else:
                    listing_attributes[attribute_name] = 1
            except KeyError:
                listing_attributes[attribute_name] = None
                print("ERROR:", attribute_name)

        if listing.get('search_text') is None:
            listing_attributes['description'] = None

        else:
            try:
                description = listing['search_text'].split('$FurnitureInfo')[1]
            except IndexError:
                description = listing['search_text'].split('$TotalFloor_text')[1]
                description = description.split('$Floor_text')[0]
            else:
                description = description.split('$Floor_text')[0]
                if listing_attributes['realtor_name'] is not None:
                    try:
                        description = description.split(listing_attributes['realtor_name'])
                        description = description[0] + description[1]
                    except IndexError:
                        pass
            if isinstance(description, list):
                description = description[0]

            listing_attributes['description'] = description
        try:
            if listing['realtor_name'] is None:
                listing_attributes['realtor'] = 0
        except KeyError:
            listing_attributes['realtor'] = 1

        listing_attributes = clean_attributes(listing_attributes)

        listing_object = ListingConstructor()
        listing_object.add_attributes(**listing_attributes)
        listing_list.append(listing_object)

    return listing_list


def parse_extra_info(extra_info, listing):
    """
    Parses a listing's extra info (total_floors, descriptions, vaad_bayit)
    Returns: listing
    """
    # print(listing.listing_id)
    # convert the raw string into a regular string so it can be decoded properly
    extra_info = extra_info.replace(r'\/', ' ').replace(r'\r', ' ').replace(r'\n', ' ')
    extra_info = codecs.decode(extra_info, 'unicode_escape')
    # print(extra_info)

    end = re.search('"HouseCommittee":', extra_info).end()
    vaad_bayit = extra_info[end:].split(',')[0].replace('₪', '').replace(',', '').replace(' ', '').replace('"', '')
    # vaad_bayit = re.findall('[0-9]+', vaad_bayit)[0]
    if vaad_bayit == 'לאצוין' or vaad_bayit == '""':
        vaad_bayit = None

    end = re.search('"TotalFloor_text":', extra_info).end()
    building_floors = extra_info[end:].split(',')[0].replace('"', '')
    try:
        int(building_floors)
    except (TypeError, ValueError):
        building_floors = None

    end = re.search('"furniture_info":', extra_info).end()
    furniture_description = str(extra_info[end:].split(',"garden_area":')[0])
    if furniture_description == '""':
        furniture_description = None

    end = re.search('"info_text":', extra_info).end()
    description = str(extra_info[end:].split('"info_title":')[0][:-1])
    if description == '""':
        description = None

    # vaad bayit is calculated monthly
    end = re.search('"property_tax":', extra_info).end()
    arnona = int(extra_info[end:].split(',"record_id":')[0].replace('₪', '').replace(',', '').replace(' ', '').replace('"',''))
    arnona = arnona/2

    # print("vaad bayit", str(vaad_bayit))
    # print("building floors", str(building_floors))
    # print("furniture description", str(furniture_description))
    # print("description", str(description))
    # print("arnona", str(arnona))

    listing.add_attributes(vaad_bayit=vaad_bayit, building_floors=building_floors,
                           furniture_description=furniture_description, description=description, arnona=arnona,
                           extra_info=1)

    return listing
