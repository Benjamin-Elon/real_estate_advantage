import sqlite3
import os
from datetime import datetime


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

    CREATE TABLE Listings (
        area_name STRING,
        top_area_name STRING,
        area_id INT,
        city_code INT,
        city_name STRING,
        neighborhood STRING, 
        street STRING,
        building_number INT,
        price INT,
        date_added STRING,
        entry_date STRING,
        updated_at STRING,
        customer_id INT,
        contact_name STRING,
        listing_id STRING,
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
        extra_info INT
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


def check_id_in_db(listing):
    cur.execute('SELECT extra_info FROM Listings WHERE (listing_id) IS (?)', (listing.listing_id,))
    result = cur.fetchone()
    if result is None:
        return False
    elif result != 1:
        return True


def remove_empty_values(dictionary):
    for key, value in dictionary.copy().items():
        if dictionary[key] is None:
            del dictionary[key]
    return dictionary


def add_listings(listing_list):
    for lst in listing_list:

        all_attrs_dict = lst.__dict__

        # remove None values from all_attrs_dict. Otherwise SQL will complain.
        all_attrs_dict = remove_empty_values(all_attrs_dict)

        cur.execute('SELECT * FROM Listings WHERE listing_id IS (?)', (lst.listing_id,))
        result = cur.fetchone()

        # if the id is not in the database, add the listing
        if result is None:
            query = "INSERT INTO Listings " + str(tuple(all_attrs_dict.keys())) \
                    + " VALUES" + str(tuple(all_attrs_dict.values())) + ";"
            # print(query)
            try:
                print("Adding listing:", lst.listing_id)
                cur.execute(query)
            except sqlite3.OperationalError:
                print("sql error on query:", print(all_attrs_dict.items()))
                pass

        conn.commit()

    return
