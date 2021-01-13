import json
from datetime import datetime


class ListingConstructor:

    def __init__(self):

        self.area_name = None
        self.top_area_id = None
        self.area_id = None
        self.city_name = None
        self.neighborhood = None
        self.street = None
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
        self.like_count = None
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
        self.description = None

    def add_attributes(self, **kwargs):

        for key, value in kwargs.items():
            if value is None:
                continue
            else:
                convert_values(value)
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
            try:
                value = float(value)
            except ValueError:
                return value

    return value


def clean_attributes(listing_attributes):
    listing_attributes['price'] = listing_attributes['price'].replace('₪', '').strip()

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
    listing_list = []

    response = response.text
    response_dict = json.loads(response)
    feed = response_dict["feed"]
    feedlist = feed["feed_items"]
    for item in feedlist:
        print(item, '\n')

    listing_items = [['area_name', 'AreaID_text'], ['top_area_name', 'topAreaID_text'], ['area_id', 'area_id'],
                     ['city_code', 'city_code'], ['city_name', 'city'], ['neighborhood', 'neighborhood'],
                     ['street', 'street'],
                     ['building_number', 'address_home_number'], ['price', 'price'], ['date_added', 'date_added'],
                     ['entry_date', 'date_of_entry'], ['updated_at', 'updated_at'], ['customer_id', 'customer_id'],
                     ['contact_name', 'contact_name'], ['listing_id', 'id'], ['category_id', 'cat_id'],
                     ['subcategory_id', 'subcat_id'], ['ad_number', 'ad_number'], ['like_count', 'like_count'],
                     ['realtor_name', 'merchant_name'], ['apt_type', 'HomeTypeID_text'],
                     ['apartment_state', 'AssetClassificationID_text'], ['sqmt', 'square_meters'],
                     ['rooms', 'Rooms_text']]

    bool_attributes = [['AirConditioner_text', 'ac'], ['mamad_text', 'b_shelter'], ['Furniture_text', 'furniture'],
                       ['Tadiran_text', 'central_ac'], ['sunpatio_text', 'sunroom'], ['storeroom_text', 'storage'],
                       ['handicapped_text', 'accesible'], ['Parking_text', 'parking'], ['PetsInHouse_text', 'pets'],
                       ['Grating_text', 'window_bars'], ['Elevator_text', 'elevator'],
                       ['yehidatdiur_text', 'sub_apartment'], ['Meshupatz_text', 'renovated'],
                       ['LongTerm_text', 'long_term'], ['PandorDoors_text', 'pandora_doors'],
                       ['patio_text', 'balconies']]

    x = 0

    for listing in feedlist:
        print("\nListing:", x)
        x += 1

        # remove irrelevant keys
        if listing.get('type') == 'advanced_ad' or listing.get('type') == 'middle_strip' \
                or listing.get('type') == 'innerRich' or listing.get('type') == 'agency_buttons':
            continue
        elif listing.get('title') == 'דירות להשכרה מתיווך':
            continue
        elif listing.get('text') == 'לא נמצאו תוצאות':
            continue

        listing_attributes = {}

        # parse out all the listings attributes
        for attribute_name, key in listing_items:
            try:
                listing_attributes[attribute_name] = listing[key]
                print(attribute_name, ":", listing_attributes[attribute_name])
            except KeyError:
                listing_attributes[attribute_name] = None
                print("ERROR:", attribute_name)
        try:
            listing_attributes['latitude'] = listing['coordinates']['latitude']
            print('latitude:', listing_attributes['latitude'])
        except KeyError:
            print("FAIL: latitude")
        try:
            listing_attributes['longitude'] = listing['coordinates']['longitude']
            print('longitude:', listing_attributes['longitude'])
        except KeyError:
            print("FAIL: longitude")

        try:
            listing_attributes['floor'] = listing['row_4'][1]['value']
            print('floor:', listing_attributes['floor'])
        except KeyError:
            print("FAIL: floor")

        for key, attribute_name in bool_attributes:
            try:
                if listing[key] == '':
                    listing_attributes[attribute_name] = 0
                else:
                    listing_attributes[attribute_name] = 1
                print(attribute_name, ":", listing_attributes[attribute_name])
            except KeyError:
                listing_attributes[attribute_name] = None
                print("ERROR:", attribute_name)

        if listing.get('search_text') is None:
            print("NO DESCRIPTION...fetching")
            listing_attributes['description'] = "there isn't"

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

            print('description:', description)
            listing_attributes['description'] = description

        listing_attributes = clean_attributes(listing_attributes)

        listing_object = ListingConstructor()
        listing_object.add_attributes(**listing_attributes)
        listing_list.append(listing_object)

    return listing_list
