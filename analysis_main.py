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

    x = input("Select action:\n"
              "(1) Create analysis settings\n"
              "(2) load analysis settings\n")
    if x == '1':
        settings = {}
        settings = location_settings(settings)
        settings = set_constraints(settings)
        listings, upper_name_column, lower_name_column = get_listings(settings)
        listings = filter_on_constraints(listings)
        select_analysis_type(listings, upper_name_column, lower_name_column)
        x = input("Would you like to save the current areas and constraints? (not including stat settings) (y/n)\n")
        if x == 'y':
            settings_manager.save_settings(settings)
    elif x == '2':
        settings = settings_manager.load_settings()
        listings, upper_name_column, lower_name_column = get_listings(settings)
        listings = filter_on_constraints(listings)
        select_analysis_type(listings, upper_name_column, lower_name_column)

    else:
        print("invalid input")
        top_menu()


def location_settings(settings):
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
    area_ids = []
    # TODO: make this nicer
    for scope_name, df in scopes:
        name_column, id_column, prev_id_column = scope_columns[scope_name]
        print(name_column, id_column, prev_id_column)

        if not area_ids:
            # select upper area ids
            area_names = list(zip(df[name_column], df[id_column]))
            area_settings = menu_select(area_names)
            area_settings.append(area_ids)

        else:
            lower_ids = []
            # for each selected upper area
            for area_id, area_name in area_ids:
                # filter df for areas in upper area
                df_1 = df[df[prev_id_column] == area_id]
                area_names = list(zip(df_1[name_column], df_1[id_column]))
                area_ids = menu_select(area_names)
                lower_ids.append(area_ids)

            area_settings.append(lower_ids)

    settings['area_settings'] = area_settings
    return settings


def menu_select(area_names):
    area_selection = []
    area_names = list(enumerate(area_names))
    for num, [area_name, area_id] in area_names:
        print(area_name, '(' + str(num) + ')')

    print("Select desired areas:\n"
          "When finished, press enter or just enter for all areas")
    area_settings = []
    while True:

        x = input()

        if x == '' and area_settings == []:
            for num, [area_name, area_id] in area_names:
                area_settings.append([area_id, area_name])
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
                    area_settings.append([area_id, area_name])

    return area_settings


def set_constraints(df, settings):

    int_range_columns = ['price', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
                         'rooms', 'floor', 'building_floors',
                         'vaad_bayit', 'arnona']

    date_range_columns = ['date_added', 'entry_date', 'updated_at', 'age']

    bool_columns = ['ac', 'b_shelter',
                    'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                    'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                    'long_term', 'pandora_doors', 'roommates', 'furniture_description', 'description']

    # if you only want to see listings with extra info
    scan_state_column = ['extra_info']

    # (having a list of areas doesn't tell you where they are relative to each other, other than 'x in y')
    geo_coord_columns = ['latitude', 'longitude']

    constraints = {}

    x = input("Would you like to toss listings with roommates? (y/n) (not full prices usually)\n")
    if x == 'y':
        df = df.loc[df['roommates'] == 0]
        constraints['roommates'] = False

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

    settings['constraints'] = constraints
    return settings


def set_range(range_str, column):
    low, high = range_str.split('-')
    try:
        int(low), int(high)
    except (ValueError, TypeError):
        print('invalid input')
        range_str = input("set valid range for" + column + ":\n")

        low, high = set_range(range_str, column)

    return low, high


def get_listings(settings):
    """Fetches the listings from database using the area settings"""

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']], [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130, 'אזור']]]]

    area_settings = settings['area_settings']

    listings = {}
    df = pd.read_sql('SELECT * FROM Listings', con)

    df = analysis_functions.generate_composite_params(df)

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

    elif x == '9':
        columns = list(enumerate(columns))
        for num, column in columns:
            print("(" + str(num) + ")", column)

        x = columns[int(input("Select a parameter:\n"))]
        axis = columns[x]

    print(axis)

    return axis


def apartment_search():
    pass
