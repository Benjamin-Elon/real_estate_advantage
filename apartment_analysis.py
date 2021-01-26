
columns = ['days_on_market', 'days_until_available', 'updated_at']
sort_types = []

def apartment_search(listings, upper_name_column, lower_name_column):
    x = input("Select action:\n"
              "(1) Create new search profile"
              "(2) Load an existing profile")

    if x == '1':
        create_search_profile()
    elif x == '2':
        load_search_profile()
        pass


def create_search_profile():


    pass


def load_search_profile():
    pass