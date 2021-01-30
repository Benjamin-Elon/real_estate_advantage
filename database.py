import sqlite3
import os
from datetime import datetime


def dict_factory(cursor, row):
    """Causes sqlite to return dictionary instead of tuple"""
    """Easier and more pythonic than using indices"""

    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# connects to database on startup.
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

todays_date = datetime.now()
todays_date_str = datetime.strftime(todays_date, '%Y-%m-%d')
todays_date = datetime.strptime(todays_date_str, '%Y-%m-%d').date()


def close_database():
    cur.close()
    return


def create_database():
    cur.executescript('''

    CREATE TABLE Listings (
    top_area_name         TEXT,
    top_area_id           INTEGER,
    area_name             TEXT,
    area_id               INTEGER,
    city_name             TEXT,
    city_id               INTEGER,
    neighborhood_name     TEXT,
    neighborhood_id       INTEGER,
    street_name           TEXT,
    street_id             INTEGER,
    building_number       INTEGER,
    price                 INTEGER,
    date_added            TEXT,
    entry_date            TEXT,
    updated_at            TEXT,
    customer_id           INTEGER,
    contact_name          TEXT,
    listing_id            TEXT    PRIMARY KEY
                                  UNIQUE
                                  NOT NULL,
    category_id           INTEGER,
    subcategory_id        INTEGER,
    ad_number             INTEGER,
    like_count            INTEGER,
    realtor_name          TEXT,
    apt_type              TEXT,
    apartment_state       TEXT,
    balconies             INTEGER,
    sqmt                  INTEGER,
    rooms                 INTEGER,
    latitude              REAL,
    longitude             REAL,
    floor                 INTEGER,
    ac                    INTEGER,
    b_shelter             INTEGER,
    furniture             INTEGER,
    central_ac            INTEGER,
    sunroom               INTEGER,
    storage               INTEGER,
    accesible             INTEGER,
    parking               INTEGER,
    pets                  INTEGER,
    window_bars           INTEGER,
    elevator              INTEGER,
    sub_apartment         INTEGER,
    renovated             INTEGER,
    long_term             INTEGER,
    pandora_doors         INTEGER,
    roommates             INTEGER,
    building_floors       INTEGER,
    vaad_bayit            INTEGER,
    furniture_description TEXT,
    description           TEXT,
    arnona                REAL,
    scanned               INTEGER,
    extra_info            INTEGER,
    id                    INTEGER UNIQUE,
    UNIQUE (
        street_id,
        building_number,
        customer_id,
        sqmt,
        rooms,
        floor,
        ac,
        building_floors
    )
    ON CONFLICT ABORT
    );
    
    CREATE TABLE Top_areas (
    top_area_name TEXT    NOT NULL
                          UNIQUE,
    top_area_id   INTEGER PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT
                          REFERENCES Listings (top_area_id) ON DELETE CASCADE
                          UNIQUE
                          NOT NULL,
    latitude      REAL,
    longitude     REAL,
    UNIQUE (
        top_area_name
    )
    ON CONFLICT IGNORE
    );

    
    CREATE TABLE Areas (
    area_name   TEXT    UNIQUE
                        NOT NULL,
    area_id     INTEGER UNIQUE
                        NOT NULL
                        REFERENCES Listings (area_id) ON DELETE CASCADE
                        PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT,
    top_area_id INTEGER NOT NULL,
    latitude    REAL,
    longitude   REAL,
    UNIQUE (
        area_name,
        top_area_id
    )
    ON CONFLICT IGNORE
    );

    
    CREATE TABLE Cities (
    city_name TEXT    UNIQUE
                      NOT NULL,
    city_id   INTEGER REFERENCES Listings (city_id) ON DELETE CASCADE
                      UNIQUE
                      NOT NULL
                      PRIMARY KEY ON CONFLICT IGNORE,
    area_id   INTEGER NOT NULL,
    latitude  REAL,
    longitude REAL,
    UNIQUE (
        city_name,
        area_id
    )
    ON CONFLICT IGNORE
    );


    CREATE TABLE Neighborhoods (
    neighborhood_name TEXT    NOT NULL,
    neighborhood_id   INTEGER REFERENCES Listings (neighborhood_id) ON DELETE CASCADE
                              NOT NULL
                              UNIQUE
                              PRIMARY KEY ON CONFLICT IGNORE,
    city_id           INTEGER NOT NULL,
    latitude          REAL,
    longitude         REAL,
    UNIQUE (
        neighborhood_name,
        city_id
    )
    ON CONFLICT IGNORE
    );


    CREATE TABLE Streets (
    street_name TEXT    NOT NULL,
    street_id   INTEGER UNIQUE
                        NOT NULL
                        REFERENCES Listings (street_id) ON DELETE CASCADE
                        PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT,
    city_id     INTEGER NOT NULL,
    latitude    REAL,
    longitude   REAL,
    UNIQUE (
        street_name,
        city_id
    )
    ON CONFLICT IGNORE
    );
    

    CREATE TABLE Listing_history (
    Listing_id     TEXT REFERENCES Listings (listing_id) 
                        UNIQUE
                        NOT NULL,
    dates_searched BLOB NOT NULL
    );

    CREATE TABLE Locale_data (
    top_area_id     INTEGER REFERENCES Top_areas (top_area_id) 
                            UNIQUE,
    area_id         INTEGER REFERENCES Areas (area_id) 
                            UNIQUE,
    city_id         INTEGER REFERENCES Cities (city_id) 
                            UNIQUE,
    neighborhood_id INTEGER REFERENCES Neighborhoods (neighborhood_id) 
                            UNIQUE,
    street_id       INTEGER REFERENCES Streets (street_id) 
                            UNIQUE,
    avg_price       BLOB    NOT NULL
                            DEFAULT "",
    price_per_sqmt  BLOB    NOT NULL
                            DEFAULT "",
    n_listings      BLOB    NOT NULL
                            DEFAULT ""
    );

    ''')

    conn.commit()

    return


def delete_listing_table():
    cur.executescript('''
    DROP TABLE IF EXISTS Listings;
    DROP TABLE IF EXISTS Listing_history;
    ''')
    conn.commit()
    create_database()


# ___unused___
def delete_locale_tables():
    cur.executescript('''   
    DROP TABLE IF EXISTS Top_areas;
    DROP TABLE IF EXISTS Areas;
    DROP TABLE IF EXISTS Cities;
    DROP TABLE IF EXISTS Neighborhoods;
    DROP TABLE IF EXISTS Streets;
    DROP TABLE IF EXISTS Locale_data;
    ''')
    conn.commit()
    create_database()

    return


def check_extra_conditions(listing):
    """Check some conditions to see if we want that extra info.
    returns True is we want it"""

    # listing_id is not is the database: random chance to get info
    cur.execute('SELECT extra_info FROM Listings WHERE (listing_id) IS (?)', (listing.listing_id,))
    result = cur.fetchone()
    # if its been scanned, but no extra info; continue
    if result is not None:
        if result['extra_info'] == 0:
            pass
        else:
            return False
    else:
        return False

    if listing.neighborhood_name is None:
        return False

    # we want to fetch arnona if we don't have enough samples for a neighborhood
    cur.execute('SELECT arnona FROM Listings WHERE (city_name, neighborhood_name) IS (?,?)', (listing.city_name, listing.neighborhood_name))
    result = cur.fetchall()
    x = 0
    if result is not None:
        for item in result:
            for k, v in item.items():
                if v is None:
                    pass
                else:
                    x += 1

    if result is None or x < 30:
        print("results for arnona:", x, listing.neighborhood_name, listing.city_name)
        return True
    else:
        # print("results for arnona:", x, listing.neighborhood_name, listing.city_name, listing.listing_id)
        return False


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

    while True:
        try:
            if lst.top_area_name is not None:
                cur.execute('INSERT OR IGNORE INTO Top_areas (top_area_name) VALUES (?)', (lst.top_area_name,))
                cur.execute('SELECT top_area_id FROM Top_areas WHERE top_area_name = (?)', (lst.top_area_name,))
                result = cur.fetchone()
                lst.top_area_id = result['top_area_id']
                break
        except sqlite3.OperationalError:
            input("Database is locked. Press enter to continue")
            continue

    if lst.area_name is not None and lst.area_name != '':
        cur.execute('INSERT OR IGNORE INTO Areas (area_name ,top_area_id) VALUES (?,?)',
                    (lst.area_name, lst.top_area_id))
        cur.execute('SELECT area_id FROM Areas WHERE (area_name, top_area_id) = (?,?)',
                    (lst.area_name, lst.top_area_id))
        result = cur.fetchone()
        lst.area_id = result['area_id']
    if lst.city_name is not None and lst.city_name != '':
        cur.execute('INSERT OR IGNORE INTO Cities (city_name ,area_id) VALUES (?,?)',
                    (lst.city_name, lst.area_id))
        cur.execute('SELECT city_id FROM Cities WHERE (city_name, area_id) = (?,?)',
                    (lst.city_name, lst.area_id))
        result = cur.fetchone()
        # print(city_id, lst.listing_id)
        try:
            lst.city_id = result['city_id']
        except TypeError:
            print("Error on city_id?\n", lst.__dict__)

    # TODO: test this
    # fill in neighborhood name in cases where neighborhood is missing, but street and city are not
    if lst.neighborhood_name is None and lst.street_name is not None and lst.city_name is not None:
        cur.execute('SELECT neighborhood_name FROM Listings WHERE (street_name, city_name) = (?,?)',
                    (lst.street_name, lst.city_name))

        result = cur.fetchone()
        if result is not None:
            lst.neighborhood_name = result['neighborhood_name']

    if lst.neighborhood_name is not None and lst.neighborhood_name != '':
        cur.execute('INSERT OR IGNORE INTO Neighborhoods (neighborhood_name ,city_id) VALUES (?,?)',
                    (lst.neighborhood_name, lst.city_id))
        cur.execute('SELECT neighborhood_id, neighborhood_name FROM Neighborhoods WHERE (neighborhood_name, '
                    'city_id) = (?,?)', (lst.neighborhood_name, lst.city_id))
        result = cur.fetchone()

        if result is not None:
            lst.neighborhood_id = result['neighborhood_id']
            lst.neighborhood_name = result['neighborhood_name']

    if lst.street_name is not None and lst.street_name != '':
        cur.execute('INSERT OR IGNORE INTO Streets (street_name, city_id) VALUES (?,?)',
                    (lst.street_name, lst.city_id))
        cur.execute('SELECT street_id, street_name FROM Streets WHERE (street_name, city_id) = (?,?)',
                    (lst.street_name, lst.city_id))
        result = cur.fetchone()
        if result is not None:
            lst.street_id = result['street_id']
            lst.street_name = result['street_name']

    conn.commit()

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
                    query = 'UPDATE OR IGNORE Listings SET ' + attribute + ' = (?) WHERE listing_id = (?)'
                    cur.execute(query, (value, lst.listing_id))
                except sqlite3.OperationalError:
                    print('sqlite3.OperationalError:', attribute, value, lst.listing_id)
                except sqlite3.IntegrityError:
                    print('sqlite3.IntegrityError: unique constraint failed.', lst.street_id, lst.building_number,
                          lst.customer_id, lst.sqmt, lst.rooms, lst.floor, lst.ac, lst.building_floors)

        elif lst.extra_info == 1:
            for attribute, value in all_attrs_dict.items():
                try:
                    query = 'UPDATE Listings SET ' + attribute + ' = (?) WHERE listing_id = (?)'
                    cur.execute(query, (value, lst.listing_id))
                except sqlite3.OperationalError:
                    print('sqlite3.OperationalError:', attribute, value, lst.listing_id)
                except sqlite3.IntegrityError:
                    print('sqlite3.IntegrityError: unique constraint failed.', lst.street_id, lst.building_number,
                          lst.customer_id, lst.sqmt, lst.rooms, lst.floor, lst.ac, lst.building_floors)

        conn.commit()

    return
