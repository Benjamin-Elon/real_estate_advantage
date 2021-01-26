import sqlite3

column_dict = {('Cheapest', 'Most expensive'): ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'price_per_sqmt'],
               ('Fewest', 'Most'): ['days_on_market', 'days_until_available', 'days_on_market']}

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()


def fetch_results(search_profile):

    search_results = {}
    for column_name, options in search_profile.items():


    pass


def apartment_search(listings, upper_name_column, lower_name_column):

    while True:
        x = input("Select action:\n"
                  "(1) Create new search profile"
                  "(2) Load an existing profile")
        if x == '1':
            search_profile = create_search_profile()
            break
        elif x == '2':
            # TODO finish this
            search_profile = load_search_profile()
            break
        else:
            print("Invalid selection...")

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
                    break
                except (ValueError, TypeError):
                    print("Invalid selection...")

    return search_profile


create_search_profile()


def load_search_profile():
    search_profile = {}
    return search_profile
