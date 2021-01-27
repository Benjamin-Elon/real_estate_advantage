import sqlite3
import settings_manager
import pandas as pd

column_dict = {('Cheapest', 'Most expensive'): ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'price_per_sqmt'],
               ('Fewest', 'Most'): ['days_on_market', 'days_until_available', 'days_on_market']}

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()


def fetch_results(search_profile, listings, upper_name_column, lower_name_column):

    search_results = {}
    for column_name, options in search_profile.items():
        low_or_high, option_name, n_results = options

        # apply the filters for each selected locale
        for upper_area_name, df in listings.items():
            if low_or_high == 'low':
                df.sort_values(column_name, ascending=False)
            elif low_or_high == 'high':
                df.sort_values(column_name, ascending=True)
                selected_listings = df[:n_results]

                for num, listing in list(enumerate(selected_listings)):
                    print(print(listing), type(listing))


    pass


def apartment_search(listings, upper_name_column, lower_name_column):

    while True:
        x = input("Select action:\n"
                  "(1) Create new search profile"
                  "(2) Load an existing profile")
        if x == '1':
            search_profile = create_search_profile()
            settings_manager.save_settings(search_profile, 'search_profile')
        elif x == '2':
            search_profile = settings_manager.load_settings('search_profile')
        else:
            print("Invalid selection...")
            continue
        break

    fetch_results(search_profile, listings, upper_name_column, lower_name_column)


def create_search_profile():
    search_profile = {}
    count = 1
    for options, column_names in column_dict.items():

        for column_name in column_names:
            print("(" + str(count) + "/6)")
            low_option, high_option = options

            count += 1
            while True:
                x = input("Set option:\n"
                          "(1) " + low_option + " [" + column_name + "]\n"
                          "(2) " + high_option + " [" + column_name + "]\n"
                          "(3) Pass\n")

                if x == '1':
                    search_profile[column_name] = ['low', low_option]
                    break
                elif x == '2':
                    search_profile[column_name] = ['high', high_option]
                    break
                elif x == '3':
                    search_profile[column_name] = None
                    break
                else:
                    print("Invalid selection...")

            while True:
                num = input("Set number of results for[" + column_name + "]:\n")
                try:
                    num = int(num)
                    search_profile[column_name].append(num)
                    break
                except (ValueError, TypeError):
                    print("Invalid selection...")

    return search_profile
