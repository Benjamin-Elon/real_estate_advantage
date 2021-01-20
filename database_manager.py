import sqlite3
import os
from datetime import datetime


# Causes sqlite to return dictionary instead of tuple
import parse_listings


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# connects to database.
# returns create if the database didn't exist
print("connecting to database...")
create = False
if not os.path.exists("yad2db.sqlite"):
    print("No database. Building...")
    create = True

conn = sqlite3.connect(r"yad2db.sqlite")
conn.row_factory = dict_factory
cur = conn.cursor()
print("Done.")

# TODO improve this to use datetime not datetime.datetime
todays_date = datetime.now()
todays_date_str = datetime.strftime(todays_date, '%Y-%m-%d')
todays_date = datetime.strptime(todays_date_str, '%Y-%m-%d').date()


def close_database():
    cur.close()
    return


def create_database():
    cur.executescript('''

    CREATE TABLE Listings (
        top_area_name STRING,
        top_area_id INT,
        area_name STRING,
        area_id INT,
        city_name STRING,
        city_id INT,
        neighborhood_name STRING, 
        neighborhood_id INT,
        street_name STRING,
        street_id INT,
        building_number INT,
        price INT,
        date_added STRING,
        entry_date STRING,
        updated_at STRING,
        customer_id INT,
        contact_name STRING,
        listing_id STRING UNIQUE,
        category_id INT,
        subcategory_id INT,
        ad_number INT,
        like_count INT,
        realtor_name STRING,
        apt_type STRING,
        apartment_state STRING,
        balconies INT,
        sqmt INT,
        rooms INT,
        latitude FLOAT,
        longitude FLOAT,
        floor INT,
        ac INT,
        b_shelter INT,
        furniture INT,
        central_ac INT,
        sunroom INT,
        storage INT,
        accesible INT,
        parking INT,
        pets INT,
        window_bars INT,
        elevator INT,
        sub_apartment INT,
        renovated INT,
        long_term INT,
        pandora_doors INT,
        roommates INT,
        building_floors INT,
        vaad_bayit INT,
        furniture_description STRING,
        description STRING,
        arnona INT,
        scanned INT,
        extra_info INT,
    );
    
    CREATE TABLE Top_areas (
    top_area_name STRING UNIQUE,
    top_area_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE
    );
    
    CREATE TABLE Areas (
    area_name STRING UNIQUE,
    area_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    top_area_id INT
    );
    
    CREATE TABLE Cities (
    city_name STRING UNIQUE,
    city_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    area_id INT
    );
    
    CREATE TABLE Neighborhoods (
    neighborhood_name STRING,
    neighborhood_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    city_id INT,
    CONSTRAINT unq UNIQUE (neighborhood_name, city_id)
    );
    
    CREATE TABLE Streets (
    street_name STRING,
    street_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    city_id INT,
    CONSTRAINT unq UNIQUE (street_name, city_id)
    );
    ''')

    conn.commit()

    return


def reset_database():
    cur.executescript('''
    DROP TABLE IF EXISTS Search_url;
    DROP TABLE IF EXISTS Listings;
    DROP TABLE IF EXISTS Listing_history;
    DROP TABLE IF EXISTS Top_areas;
    DROP TABLE IF EXISTS Areas;
    DROP TABLE IF EXISTS Cities;
    DROP TABLE IF EXISTS Neighborhoods;
    DROP TABLE IF EXISTS Streets;
    ''')

    conn.commit()

    create_database()

    return


def check_extra_info(listing):
    cur.execute('SELECT extra_info, scanned FROM Listings WHERE (listing_id) IS (?)', (listing.listing_id,))
    result = cur.fetchone()
    # listing_id is not is the database: random chance to get info
    return result, listing.listing_id


def remove_empty_values(dictionary):
    for key, value in dictionary.copy().items():
        if dictionary[key] is None:
            del dictionary[key]
        elif dictionary[key] == '':
            del dictionary[key]
            # print(key, value)
    return dictionary


def get_primary_keys(lst):
    # print(lst.listing_id)
    if lst.area_id == 16 or lst.area_id == 0:
        return
        # # get the area id using city name
        # print(lst.listing_id)
        # cur.execute('SELECT area_id FROM Cities WHERE (city_name) = (?)', (lst.city_name,))
        # area_id = cur.fetchone()
        # lst.area_id = area_id['area_id']
        # # print(area_id, lst.listing_id)
        #
        # # get the area name and top area id using the area_id
        # cur.execute('SELECT area_name, top_area_id FROM Areas WHERE (area_id) = (?)', (lst.area_id,))
        # area_names = cur.fetchone()
        # lst.area_name = area_names['area_name']
        # lst.top_area_id = area_names['top_area_id']
        # # print(area_names)
        #
        # cur.execute('SELECT top_area_name FROM Top_areas WHERE (top_area_id) = (?)', (lst.area_id,))
        # top_area_name = cur.fetchone()
        # lst.top_area_name = top_area_name['top_area_name']
    # print(lst.listing_id)
    if lst.top_area_name is not None:
        cur.execute('INSERT OR IGNORE INTO Top_areas (top_area_name) VALUES (?)', (lst.top_area_name,))
        cur.execute('SELECT top_area_id FROM Top_areas WHERE top_area_name = (?)', (lst.top_area_name,))
        top_area_id = cur.fetchone()
        lst.top_area_id = top_area_id['top_area_id']

    if lst.area_name is not None:
        cur.execute('INSERT OR IGNORE INTO Areas (area_name ,top_area_id) VALUES (?,?)',
                    (lst.area_name, lst.top_area_id))
        cur.execute('SELECT area_id FROM Areas WHERE (area_name, top_area_id) = (?,?)',
                    (lst.area_name, lst.top_area_id))
        area_id = cur.fetchone()
        lst.area_id = area_id['area_id']
    if lst.city_name is not None:
        cur.execute('INSERT OR IGNORE INTO Cities (city_name ,area_id) VALUES (?,?)',
                    (lst.city_name, lst.area_id))
        cur.execute('SELECT city_id FROM Cities WHERE (city_name, area_id) = (?,?)',
                    (lst.city_name, lst.area_id))
        city_id = cur.fetchone()
        # print(city_id, lst.listing_id)
        try:
            lst.city_id = city_id['city_id']
        except TypeError:
            lst.__dict__

    # if lst.neighborhood_name is None and lst.street_name is not None and lst.city_name is not None:
    #     cur.execute('SELECT neighborhood_name FROM Listings WHERE (street_name, city_name) = (?,?)',
    #                 (lst.street_name, lst.city_name))
    #     neighborhood_name = cur.fetchone()
    #     lst.neighborhood_name = neighborhood_name['neighborhood_name']

    if lst.neighborhood_name is not None:
        cur.execute('INSERT OR IGNORE INTO Neighborhoods (neighborhood_name ,city_id) VALUES (?,?)',
                    (lst.neighborhood_name, lst.city_id))
        cur.execute('SELECT neighborhood_id FROM Neighborhoods WHERE (neighborhood_name, city_id) = (?,?)',
                    (lst.neighborhood_name, lst.city_id))
        neighborhood_id = cur.fetchone()
        lst.neighborhood_id = neighborhood_id['neighborhood_id']

    if lst.street_name is not None:
        cur.execute('INSERT OR IGNORE INTO Streets (street_name, city_id) VALUES (?,?)',
                    (lst.street_name, lst.city_id))
        cur.execute('SELECT street_id FROM Streets WHERE (street_name, city_id) = (?,?)',
                    (lst.street_name, lst.city_id))
        street_id = cur.fetchone()
        lst.street_id = street_id['street_id']

    return lst


def add_listings(listing_list):
    for lst in listing_list:

        lst = get_primary_keys(lst)

        all_attrs_dict = lst.__dict__

        # remove None values from all_attrs_dict. Otherwise SQL will complain.
        all_attrs_dict = remove_empty_values(all_attrs_dict)

        cur.execute('SELECT * FROM Listings WHERE listing_id IS (?)', (lst.listing_id,))
        result = cur.fetchone()

        # if the id is not in the database, add the listing
        if result is None:
            cur.execute('INSERT OR IGNORE INTO Listings (listing_id) VALUES (?)', (lst.listing_id,))
            for attribute, value in all_attrs_dict.items():
                try:
                    query = 'UPDATE Listings SET ' + attribute + ' = (?) WHERE listing_id = (?)'
                    cur.execute(query, (value, lst.listing_id))
                except sqlite3.OperationalError:
                    print('sqlite3.OperationalError:', attribute, value, lst.listing_id)

            conn.commit()

    return


def area_manager():

    settings = {}
    # TODO remove _name from vars
    scopes = [['top_area_name', None], ['area_name', 'area_id'], ['city_name', 'city_id'],
              ['neighborhood', 'neighborhood_id'], ['street_name', 'street_id']]
    settings['top_area_name'] = []
    settings['area_name'] = []
    settings['city_name'] = []
    settings['neighborhood'] = []
    settings['street_name'] = []

    for scope in scopes:
        settings = area_menus(scope[0], scope[1], settings)

    return


# TODO finish this
def area_menus(scope_name, area_id, settings):

    if area_id is None:
        menu = []
        cur.execute('SELECT DISTINCT top_area_name FROM Listings')
        results = cur.fetchall()
        x = 0
        for top_area_name in results:
            if top_area_name != '':
                menu.append([x, top_area_name['top_area_name']])
                x += 1

    else:
        print(area_id, scope_name)
        cur.execute('SELECT DISTINCT (?) FROM Listings', (scope_name,))
        results = cur.fetchall()
        # print(results)
        menu = []
        for result in results:
            # some areas are site weird leftovers or site tests
            if result['area_name'] != '':
                menu.append([result['area_id'], result['area_name']])

    for x, name in menu:
        print(name, '(' + str(x) + ')')

    print("Select desired areas:\n"
          "When finished, press enter")
    x = None
    # Select as many countries as desired
    while x != '':
        try:
            x = input()
            x = menu[int(x)]
        except (KeyError, ValueError):
            print("invalid selection")
        else:
            if x in settings[scope_name]:
                print("already selected")
            else:
                settings[scope_name].append(x)

    return settings