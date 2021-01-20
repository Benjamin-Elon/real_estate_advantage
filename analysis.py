import pandas as pd
import sqlite3
from collections import defaultdict
import settings_manager

import matplotlib.pyplot as plt
import seaborn as sns

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

# TODO:
# impute arnona from average cost per neighborhood
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter


columns = ['price', 'date_added', 'entry_date',
           'updated_at', 'contact_name',
           'realtor_name', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
           'rooms', 'floor', 'building_floors',
           'vaad_bayit', 'arnona']

bool_columns = ['ac', 'b_shelter',
                'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                'long_term', 'pandora_doors', 'roommates']

other_columns = ['customer_id', 'latitude', 'longitude', 'furniture_description', 'description',
                 'scanned', 'extra_info']


def top_menu():
    x = input("Select action:"
              "(1) Create analysis settings"
              "(2) load analysis settings")
    if x == '1':
        area_ids = location_settings()
        listings = get_listings(area_ids)
        select_analysis_type(listings)
    # TODO: write load and save settings functions
    if x == '2':
        settings = settings_manager.load_settings()


def get_listings(area_ids):
    """Uses area_ids to fetch listings from database"""

    listings = defaultdict(dict)
    df = pd.read_sql('SELECT * FROM Listings', con)
    # area_ids = {'Cities': {18: {'Neighborhoods': [68, 74, 88, 113]}}}

    # outer scope
    for scope, values in area_ids.items():
        id_column, name_column = get_scope_info(scope)
        areas = values

    for area_id, values in areas.items():
        # get outer area name
        area_name = df.loc[df[id_column] == area_id, name_column].iloc[0]

        for scope_1, areas_ids in values.items():
            # get outer column names
            id_column_1, name_column_1 = get_scope_info(scope_1)

            for item in areas_ids:
                # get inner area names
                area_name_1 = df.loc[df[id_column_1] == item, name_column_1].iloc[0]
                # create df for each inner area
                listings[area_name][area_name_1] = df.loc[df[id_column_1] == item]

    # for key, value in listings.items():
    #     display_distributions(value)

    return listings


def select_analysis_type(listings):

    x = input("Select analysis type:\n"
              "(1) Apartment search\n"
              "(2) Visualization")

    if x == '1':
        apartment_search()

    elif x == '2':
        x = input("Select visualization type:\n"
                  "(1) Single Bar plot\n"
                  "(2) Distribution subplots with rugs; one per area\n"
                  "(3) Statistical relationships (scatter plots)")

        if x == '1':
            x_axis = select_x_axis()
            display_hist(listings, x_axis)
        elif x == '2':
            x_axis = select_x_axis()
            display_distributions(listings, x_axis)
        elif x == '3':
            x_axis = select_x_axis()
            y_axis = select_y_axis()
            display_scatter_plots(listings, x_axis, y_axis)


def select_x_axis():
    x = input("Select an option for distribution visualization:\n"
              "(1) Total Price(price + arnona + vaad_bayit)\n"
              "(2) Arnona/sqmt\n"
              "(3) Price/sqmt"
              "(4) Total Price/sqmt"
              "(5) Apartment Age"
              "(9) select a parameter (column) from database\n")

    if x == '1':
        pass
    elif x == '2':
        pass
    elif x == '3':
        pass
    elif x == '4':
        pass
    elif x == '5':
        pass
    elif x == '9':
        pass


    x_axis = None

    return x_axis


def select_y_axis():
    x = input("Select an option for distribution visualization:\n"
              "(1) Price + arnona + vaad_bayit\n"
              "(2) Price\n"
              "(3) Arnona\n"
              "(4) Arnona/sqmt\n"
              "(5) Apartment size (sqmt)"
              "(6) select parameter(column) from database\n")

    y_axis = None

    return y_axis


def display_hist(listings):
    pass


def display_distributions(listings, x_axis):
    fig, ax = plt.subplots(len(listings), 1, figsize=(10, 10))
    x = 0
    for area_name, df in listings.items():
        area_name = area_name[::-1]
        price = df['price']
        average_price = price.mean()
        print("average price for ", area_name, ":", average_price)

        sns.displot(price, ax=ax[x], kind="kde", rug=True)
        ax[x].set_title(area_name)
        x += 1
    plt.show()


def display_scatter_plots(areas):
    pass


def apartment_search():
    pass


def get_scope_info(scope):
    """helper for locations_settings."""

    dict_1 = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
              'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
              'Streets': ['street_id', 'street_name']}
    scope_info = dict_1.get(scope)
    id_column = scope_info[0]
    name_column = scope_info[1]

    return id_column, name_column


def location_settings():
    """Users can select two tiers of areas. 
    Protect the user from themselves. Makes no sense to compare a scale to a totally different scale."""

    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
    df_areas = pd.read_sql('SELECT * FROM Areas', con)
    df_cities = pd.read_sql('SELECT * FROM Cities', con)
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con)
    df_streets = pd.read_sql('SELECT * FROM Streets', con)

    # {{name: [name_column, id_column, identifying_column, scope_df]},...}
    scopes = {'Top_areas': ['top_area_name', 'top_area_id', 'top_area_id', df_top_areas],
              'Areas': ['area_name', 'area_id', 'top_area_id', df_areas],
              'Cities': ['city_name', 'city_id', 'area_id', df_cities],
              'Neighborhoods': ['neighborhood_name', 'neighborhood_id', 'city_id', df_neighborhoods],
              'Streets': ['street_name', 'street_id', 'city_id', df_streets]}
    scope_names = ['Top_areas', 'Areas', 'Cities', 'Neighborhoods', 'Streets']

    num = 0
    for name in scope_names:
        print('(' + str(num) + ')', name)
        num += 1

    x = input("Select the scale you would like to compare:\n")
    # TODO: fix so you can compare top_areas
    if x == 0:
        pass
    # select scope and the one above
    scope_names = scope_names[int(x) - 1:int(x) + 1]

    area_ids = {}

    scope_name = scope_names[0]
    name_column, id_column, prev_id_column, df = scopes[scope_name]
    area_ids[scope_name] = {}
    # select areas for scope
    area_names = list(df[name_column])
    menu = list(enumerate(area_names))
    area_ids = select_areas_menu(menu, df, name_column, id_column)

    # set column names and dataframes for next scope
    scope_name_1 = scope_names[1]
    name_column_1, id_column_1, prev_id_column, df_1 = scopes[scope_name_1]

    for area_id in area_ids:
        # crate empty dict for each top area
        area_ids[scope_name][area_id] = {}

    # for each selected top area
    for area_id in area_ids:
        df_2 = df_1.loc[(df_1[prev_id_column] == area_id)]
        area_names_1 = df_2[name_column_1]
        menu = list(enumerate(area_names_1))
        sub_area_ids = select_areas_menu(menu, df_2, name_column_1, id_column_1)

        area_ids[scope_name][area_id][scope_name_1] = sub_area_ids

    print(area_ids)

    return area_ids


def select_areas_menu(menu, df, prev_id_column, id_column):
    area_selection = []
    area_ids = []

    for num, name in menu:
        if name != '':
            print(name, '(' + str(num) + ')')

    print("Select desired areas:\n"
          "When finished, press enter or just enter for all areas")

    while True:
        x = input()

        if x == '' and area_selection == []:
            for num, area in menu:
                print(area)
                area_id = int(df.loc[df[prev_id_column] == area, id_column])
                print(area_id)
                area_ids.append(area_id)
            break
        elif x == '':
            break

        # if valid area is selected, add it to the scope list
        else:
            try:
                x = int(x)
                area = menu[x][1]
            except (ValueError, KeyError, IndexError):
                print("invalid selection")
            else:
                if area in area_selection:
                    print("already selected")
                else:
                    area_selection.append(area)

    # for each  selected area, get the area_id
    for area in area_selection:
        area_id = int(df.loc[df[prev_id_column] == area, id_column])
        # print(area_id)
        area_ids.append(area_id)

    return area_ids


top_menu()
