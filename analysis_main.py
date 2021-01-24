import pandas as pd
import sqlite3
from collections import defaultdict

import analysis_functions
import settings_manager

import matplotlib.pyplot as plt
import seaborn as sns

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

# TODO:
# impute arnona from average cost per neighborhood
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter


# TODO: use coordinates to filter for listings closest to coordinates or list of coordinates
def update_geo_coords():
    # generate average coordinates for each locale and max-min for lat and long coordinates
    return


def top_menu():

    update_geo_coords()
    df = pd.read_sql('SELECT * FROM Listings', con)
    df = analysis_functions.generate_composite_params(df)

    x = input("Select action:\n"
              "(1) Create analysis settings\n"
              "(2) load analysis settings\n")
    if x == '1':
        settings = {}
        settings['area_settings'] = location_settings()
        x = input("Set constraints? (y/n)\n")
        if x == 'y':
            df, settings['constraints'] = apply_constraints(df)
        else:
            settings['constraints'] = None

        listings, upper_name_column, lower_name_column = get_listings(df, settings)
        listings = filter_on_constraints(listings)
        select_analysis_type(listings, upper_name_column, lower_name_column)
        x = input("Would you like to save the current areas and constraints? (not including stat settings) (y/n)\n")
        if x == 'y':
            settings_manager.save_settings(settings)
    elif x == '2':
        settings = settings_manager.load_settings()
        listings, upper_name_column, lower_name_column = get_listings(df, settings)
        listings = filter_on_constraints(listings)
        select_analysis_type(listings, upper_name_column, lower_name_column)

    else:
        print("invalid input")
        top_menu()


def location_settings():
    """Users can select two tiers of areas. Any more is confusing for everyone.
    Makes no sense to compare a scale to a totally different scale."""

    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
    df_areas = pd.read_sql('SELECT * FROM Areas', con)
    df_cities = pd.read_sql('SELECT * FROM Cities', con)
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con)
    df_streets = pd.read_sql('SELECT * FROM Streets', con)

    # {{name: [name_column, id_column, identifying_column]},...}
    scope_columns = {'Top_areas': ['top_area_name', 'top_area_id', 'top_area_id'],
                     'Areas': ['area_name', 'area_id', 'top_area_id'],
                     'Cities': ['city_name', 'city_id', 'area_id'],
                     'Neighborhoods': ['neighborhood_name', 'neighborhood_id', 'city_id'],
                     'Streets': ['street_name', 'street_id', 'city_id']}
    scope_names = ['Top_areas', 'Areas', 'Cities', 'Neighborhoods', 'Streets']
    df_list = [df_top_areas, df_areas, df_cities, df_neighborhoods, df_streets]

    scopes = list(zip(scope_names, df_list))

    num = 0
    for name in scope_names:
        print('(' + str(num) + ')', name)
        num += 1

    x = input("Select the largest scale you would like to compare:\n")
    scopes = scopes[int(x):int(x) + 2]

    # first tuple in the settings is the names of the scopes
    area_settings = [[scope_names[int(x)], scope_names[int(x) + 1]]]
    area_selection = []
    # TODO: make this nicer
    for scope_name, df in scopes:
        name_column, id_column, prev_id_column = scope_columns[scope_name]
        print(name_column, id_column, prev_id_column)
        # print(name_column, id_column, prev_id_column)

        if not area_selection:
            # select upper area ids
            area_names = list(zip(df[name_column], df[id_column]))
            area_selection = menu_select(area_names)
            area_settings.append(area_selection)

        else:

            lower_ids = []
            # for each selected upper area
            for area_id, area_name in area_selection:
                print(area_id, area_name)
                # filter df for areas in upper area
                df_1 = df.loc[df[prev_id_column] == area_id]
                area_names = list(zip(df_1[name_column], df_1[id_column]))
                area_ids = menu_select(area_names)
                lower_ids.append(area_ids)

            area_settings.append(lower_ids)

    return area_settings


def menu_select(area_names):
    area_selection = []
    area_names = list(enumerate(area_names))
    for num, [area_name, area_id] in area_names:
        print(area_name, '(' + str(num) + ')')

    print("Select desired areas:\n"
          "When finished, press enter or just enter for all areas")
    area_selection = []
    while True:

        x = input()

        if x == '' and area_selection == []:
            for num, [area_name, area_id] in area_names:
                area_selection.append([area_id, area_name])
            break
        elif x == '':
            break

        # if valid selection, add it to the list
        else:
            try:
                x = int(x)
            except (ValueError, KeyError, IndexError):
                print("invalid selection")
            else:
                area_name = area_names[x][1][0]
                area_id = area_names[x][1][1]

                if area_name in area_selection:
                    print("already selected")
                else:
                    area_selection.append([area_id, area_name])

    return area_selection


def apply_constraints(df):

    int_range_columns = ['price',  'vaad_bayit', 'arnona', 'sqmt', 'balconies',
                         'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available']

    date_range_columns = ['date_added', 'updated_at']

    bool_columns = ['ac', 'b_shelter',
                    'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                    'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                    'long_term', 'pandora_doors', 'furniture_description', 'description']
    option_columns = ['apt_type', 'apartment_state']
    # if you only want to see listings with extra info
    scan_state_column = ['extra_info']

    # (having a list of areas doesn't tell you where they are relative to each other, other than 'x in y')
    geo_coord_columns = ['latitude', 'longitude']

    constraints = {}

    x = input("Toss outliers (by locale) (y/n):\n")
    if x == 'y':
        constraints['toss_outliers'] = []
        for column in int_range_columns:

            print("(examples: 3-97, 0-95")
            quantiles = input("set quantile range for" + column + ":\n")
            q_low, q_high = set_range(quantiles, column)

            q_low = df[column].quantile(q_low)
            q_high = df[column].quantile(q_high)
            # TODO: group by each neighborhood or city if neighborhood is None
            df = df
            df = df[(df[column] < q_high) & (df[column] > q_low)]
            constraints['toss_outliers'].append([column, q_low, q_high])

            return df, constraints

    x = input("Include listings with roommates? (y/n, pass:'enter') (not full prices usually)\n")
    if x == 'y':
        df = df.loc[df['roommates'] == 1]
        constraints['roommates'] = 1
    elif x == 'n':
        df = df.loc[df['roommates'] == 0]
        constraints['roommates'] = 0
    else:
        pass

    for column in bool_columns:
        x = input("Must have " + column + "? (y/n, pass:'enter')\n")
        if x == 'y':
            df = df.loc[df[column] == 1]
            constraints[column] = 1
        elif x == 'n':
            df = df.loc[df[column] == 0]
            constraints[column] = 0
        else:
            pass

    for column in int_range_columns:
        x = input("Set range for " + column + "? (y/n)\n")
        if x == 'y':
            print("(examples: 1000-2500, 0-200")
            quantiles = input("Set range for " + column + ":\n")
            low, high = set_range(quantiles, column)
            constraints[column] = [low, high]

            df = df[(df[column] < high) & (df[column] > low)]

    return df, constraints


def set_range(range_str, column):
    low, high = range_str.split('-')
    try:
        int(low), int(high)
    except (ValueError, TypeError):
        print('invalid input')
        range_str = input("set valid range for" + column + ":\n")

        low, high = set_range(range_str, column)

    return int(low), int(high)


def get_listings(df, settings):
    """Fetches the listings from database using the area settings"""

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']], [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130, 'אזור']]]]

    area_settings = settings['area_settings']

    listings = {}

    upper_scope_name, lower_scope_name = area_settings[0]
    upper_id_column = scope_names[upper_scope_name][0]
    lower_id_column = scope_names[lower_scope_name][0]
    upper_name_column = scope_names[upper_scope_name][1]
    lower_name_column = scope_names[lower_scope_name][1]

    area_settings = area_settings[1:]

    for upper_area, lower_areas in zip(area_settings[0], area_settings[1]):
        area_ids = []
        upper_name = upper_area[1]
        upper_id = upper_area[0]
        for lower_id, lower_name in lower_areas:
            area_ids.append(lower_id)
        listings[upper_name] = df.loc[df[lower_id_column].isin(area_ids) & (df[upper_id_column] == upper_id)]

    return listings, upper_name_column, lower_name_column


# TODO: write this
def filter_on_constraints(listings):

    return listings


def select_analysis_type(listings, upper_name_column, lower_name_column):
    x = input("Select analysis type:\n"
              "(1) Apartment search\n"
              "(2) Visualization\n")

    if x == '1':
        apartment_search()

    elif x == '2':

        x = input("Visualize:\n"
                  "(1) Upper scope (not done)\n"
                  "(2) Lower scope\n")

        option = ['up', 'down']
        option = option[int(x) - 1]

        x = input("Select visualization type:\n"
                  "(1) Distribution(Bar)\n"
                  "(2) Distribution(kde with rugs)\n"
                  "(3) scatter plots\n")

        if x == '1':
            y_axis = select_axis('distribution')
            analysis_functions.display_hists(listings, y_axis, option, upper_name_column, lower_name_column)
        elif x == '2':
            x_axis = select_axis('distribution')
            analysis_functions.display_distributions(listings, x_axis, option, upper_name_column, lower_name_column)
        elif x == '3':
            x_axis = select_axis('x-axis')
            y_axis = select_axis('y-axis')
            analysis_functions.display_scatter_plots(listings, x_axis, y_axis, option, upper_name_column,
                                                     lower_name_column)
    return


def select_axis(axis_type):

    columns = ['price', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
               'rooms', 'latitude', 'longitude', 'floor', 'ac', 'b_shelter',
               'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
               'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
               'long_term', 'pandora_doors', 'roommates', 'building_floors',
               'vaad_bayit', 'arnona']

    x = int(input("Select an variable for the " + axis_type + ":\n"
                  "(1) Total Price(price + arnona + vaad_bayit)\n"
                  "(2) Arnona/sqmt\n"
                  "(3) Price/sqmt\n"
                  "(4) Total Price/sqmt\n"
                  "(5) Apartment Age\n"
                  "(9) select a parameter (column) from database\n"))

    axis_list = ['total_price', 'arnona_per_sqmt', 'price_per_sqmt', 'total_price_per_sqmt', 'days_on_market']
    if x - 1 in range(len(axis_list)):
        axis = axis_list[x - 1]

    elif x == 9:
        columns = list(enumerate(columns))
        for num, column in columns:
            print("(" + str(num) + ")", column)

        axis = columns[int(input("Select a parameter:\n"))][1]
        # axis = columns[x]

    print(axis)

    return axis


def apartment_search():
    pass
