import sqlite3
import os
from datetime import datetime
import numpy as np


# Causes sqlite to return dictionary instead of tuple
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
    CREATE TABLE Search_url (
    search_url_id INTEGER PRIMARY KEY,
    search_url STRING UNIQUE,
    first_search_date STRING,
    recent_search_date STRING
    );

    CREATE TABLE Listings (
    search_url_id INT,
    search_url STRING,
    listing_id STRING UNIQUE,
    listing_url STRING UNIQUE,
    apt_type STRING,
    city_id INT,
    city STRING,
    neighborhood_id INT,
    neighborhood STRING,
    street_id INT,
    street STRING,
    image STRING,
    building_number INT,
    floor INT,
    sqmt INT,
    rooms FLOAT,
    price INT,
    num_on_page INT,
    date_posted STRING,
    most_recent_search STRING,
    listing_age INT,
    realtor STRING,
    entry_date STRING,
    vaad_bayit BLOB,
    balconies BLOB,
    building_floors INT,
    num_payments BLOB,
    arnona BLOB,
    parking_spots BLOB,
    elevator BLOB,
    renovated BLOB,
    entrance_num BLOB,
    roommates INT,
    accessible INT,
    description STRING,
    ac INT,
    central_ac INT,
    window_bars INT,
    pandora_doors INT,
    storage_unit INT,
    long_term INT,
    pets INT,
    furniture INT,
    kosher_kitchen INT,
    b_shelter INT,
    exclusive BLOB,
    extra INT,
    age INT,
    listing_rank INT,
    confidence FLOAT,
    platinum INT,
    old_id STRING,
    entry_now INT
    );
                      
    CREATE TABLE Listing_history (
    listing_id STRING,
    old_id STRING,
    date_posted STRING,
    price INTEGER,
    realtor STRING,
    listing_rank INT,
    confidence FLOAT,
    changes BLOB
    );''')

    conn.commit()

    return


def reset_database():

    cur.executescript('''
    DROP TABLE IF EXISTS Search_url;
    DROP TABLE IF EXISTS Listings;
    DROP TABLE IF EXISTS Listing_history;
    DROP TABLE IF EXISTS City;
    DROP TABLE IF EXISTS Neighborhood;
    DROP TABLE IF EXISTS Street;
    ''')

    conn.commit()

    create_database()

    return


def check_id_in_db(listings):
    not_in_db = list()
    x = 0

    for lst in listings:

        if lst.listing_id is None:
            print("no listing_id", lst.num_on_page, lst.realtor)
            continue
        cur.execute('SELECT * FROM Listings WHERE (listing_id) IS (?)', (lst.listing_id,))
        match = cur.fetchone()

        # If any of these values is None, listing is definitely not in db, and we should get extra info
        if match is None:
            not_in_db.append(lst.listing_id)

        x += 1
