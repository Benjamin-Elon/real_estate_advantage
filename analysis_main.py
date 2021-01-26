import pandas as pd
import sqlite3
from collections import defaultdict
import apartment_analysis
import analysis_functions
import settings_manager

import matplotlib.pyplot as plt
import seaborn as sns

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

# TODO: add sort by (price, alphabetical, top_x ect)
# TODO: remove area_name
# TODO: nefesh bnefesh
# impute arnona from average cost per neighborhood
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter


int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
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


def update_geo_coords():
    """generate average geographic coordinates for each locale, updates the sql database"""

    df = pd.read_sql('SELECT * FROM Listings', con)

    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
    df_areas = pd.read_sql('SELECT * FROM Areas', con)
    df_cities = pd.read_sql('SELECT * FROM Cities', con)
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con)
    df_streets = pd.read_sql('SELECT * FROM Streets', con)

    scope_names = ['Top_areas', 'Areas', 'Cities', 'Neighborhoods', 'Streets']
    id_column_names = ['top_area_id', 'area_id', 'city_id', 'neighborhood_id', 'street_id']
    df_list = [df_top_areas, df_areas, df_cities, df_neighborhoods, df_streets]

    for df_name, id_column, locale_df in list(zip(scope_names, id_column_names, df_list)):
        print("Updating: " + df_name + "...")
        # df = df.sort_values(id_column)
        # locale_df.sort_values(id_column)

        area_groups = df.groupby(id_column)
        for area_id, area_df in area_groups:
            locale_df.loc[locale_df[id_column] == area_id, 'latitude'] = area_df['latitude'].mean()
            locale_df.loc[locale_df[id_column] == area_id, 'longitude'] = area_df['longitude'].mean()
        locale_df.to_sql(df_name, con=con, if_exists='replace', index=None)

    print("done.")

    return


def top_menu():

    df = pd.read_sql('SELECT * FROM Listings', con)
    df = analysis_functions.generate_composite_params(df)

    x = input("Select action:\n"
              "(1) Create analysis settings\n"
              "(2) load analysis settings\n"
              "(3) Update geo coordinates for each locale\n"
              "(9) Return to main menu\n")

    # create settings
    if x == '1':
        settings = {}
        # select desired locales
        settings['area_settings'] = set_locales()

        x = input("Set constraints? (y/n)\n")
        if x == 'y':
            # set and apply constraints
            settings['constraints'] = set_constraints()
            df = apply_constraints(df, settings['constraints'])
        else:
            settings['constraints'] = None

        listings, upper_name_column, lower_name_column = get_listings(df, settings['area_settings'])
        select_analysis_type(listings, upper_name_column, lower_name_column)
        x = input("Would you like to save the current areas and constraints? (not including stat settings) (y/n)\n")
        if x == 'y':
            settings_manager.save_settings(settings)

    # load settings
    elif x == '2':
        settings = settings_manager.load_settings()
        # apply constraints if any
        df = apply_constraints(df, settings['constraints'])
        # get listings from db for each selected area
        listings, upper_name_column, lower_name_column = get_listings(df, settings['area_settings'])
        select_analysis_type(listings, upper_name_column, lower_name_column)

    elif x == '3':
        update_geo_coords()

    elif x == '9':
        return

    else:
        print("invalid input")

    top_menu()


def set_locales():
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


def set_constraints():

    constraints = {}

    x = input("Toss outliers (by locale) (y/n):\n")
    if x == 'y':
        constraints['toss_outliers'] = []
        for column in int_range_columns:

            print("(examples: 3-97, 0-95\n "
                  "Press enter to pass")
            quantiles = input("set quantile range for" + column + ":\n")
            if quantiles == '':
                constraints['toss_outliers'][column] = None
            else:
                q_low, q_high = set_range(quantiles, column)
                constraints['toss_outliers'][column] = [q_low, q_high]
    else:
        constraints['toss_outliers'] = None

    x = input("Include listings with roommates? (y/n, pass:'enter') (not full prices usually)\n")
    if x == 'y':
        constraints['roommates'] = 1
    elif x == 'n':
        constraints['roommates'] = 0
    else:
        constraints['roommates'] = None

    for column in bool_columns:
        x = input("Must have " + column + "? (y/n, pass:'enter')\n")
        if x == 'y':
            constraints[column] = 1
        elif x == 'n':
            constraints[column] = 0
        else:
            constraints[column] = None

    for column in int_range_columns:
        x = input("Set range for " + column + "? (y/n)\n")
        if x == 'y':
            print("(examples: 1000-2500, 0-200)")
            quantiles = input("Set range for " + column + ":\n")
            low, high = set_range(quantiles, column)
            constraints[column] = [low, high]

    return constraints


def apply_constraints(df, constraints):

    # toss outliers for each variable
    if constraints['toss_outliers'] is not None:
        df = toss_outliers(df, constraints)

    # apply range constraints
    for column in int_range_columns:
        if constraints[column] is not None:
            low, high = constraints[column]

            df = df[(df[column] < high) & (df[column] > low)]

    # bool constraints
    for column in bool_columns:
        if constraints[column] is not None:
            # value can be 0 or 1
            value = constraints[column]
            df = df.loc[df['roommates'] == value]

    return df


def set_range(range_str, column):
    low, high = range_str.split('-')
    try:
        int(low), int(high)
    except (ValueError, TypeError):
        print('invalid input')
        range_str = input("set valid range for" + column + ":\n")

        low, high = set_range(range_str, column)

    return int(low), int(high)


def toss_outliers(df, constraints):
    for column in int_range_columns:

        if constraints['toss_outliers'][column] is not None:
            q_low, q_high = constraints['toss_outliers'][column]
            q_low = df[column].quantile(q_low)
            q_high = df[column].quantile(q_high)

            # sometimes neighborhood can be none, but city always has a value.
            # group df locale, toss outliers, and append each group back together into a single df
            neighborhood = df.query('neighborhood_name != None')
            neighborhood = neighborhood.groupby(by='neighborhood_id')

            city = df.query('city_name != None & neighborhood_name == None')
            city = city.groupby(by='city_id')

            df_1 = pd.DataFrame()
            for neighborhood_id, neighborhood_df in neighborhood:
                print(len(neighborhood_df))
                neighborhood_df = neighborhood_df.loc[
                    (neighborhood_df[column] < q_high) & (neighborhood_df[column] > q_low)]
                print(len(neighborhood_df))
                df_1 = df_1.append(neighborhood_df)

            for city_id, city_df in city:
                orig_len = len(city_df)
                city_df = city_df.loc[
                    (city_df[column] < q_high) & (city_df[column] > q_low)]
                print(len(city_df))
                df_1 = df_1.append(city_df)

            df = df_1

    return df


def get_listings(df, area_settings):
    """Fetches the listings from database using the area settings"""
    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']],
    # [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130,
    # 'אזור']]]]

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

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


def select_analysis_type(listings, upper_name_column, lower_name_column):
    x = input("Select analysis type:\n"
              "(1) Apartment search\n"
              "(2) Visualization\n")

    if x == '1':
        apartment_analysis.apartment_search(listings, upper_name_column, lower_name_column)

    elif x == '2':
        str_1 = ' '
        x = input("Visualize:\n"
                  "(1) Upper scope (" + str_1.join((upper_name_column.split('_')[:-1])) + ")\n"
                  "(2) Lower scope (" + str_1.join((lower_name_column.split('_')[:-1])) + ")\n")

        option = ['up', 'down']
        option = option[int(x) - 1]

        x = input("Select visualization type:\n"
                  "(1) Distribution(Histogram)\n"
                  "(2) Distribution(kde with rugs)\n"
                  "(3) Scatter plots\n")

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
    axis_list = ['total_price', 'arnona_per_sqmt', 'price_per_sqmt', 'total_price_per_sqmt', 'days_on_market']
    columns = ['price', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
               'rooms', 'latitude', 'longitude', 'floor', 'ac', 'b_shelter',
               'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
               'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
               'long_term', 'pandora_doors', 'roommates', 'building_floors',
               'vaad_bayit', 'arnona']

    print("(1) Total Price(price + arnona + vaad_bayit)\n"
          "(2) Arnona/sqmt\n"
          "(3) Price/sqmt\n"
          "(4) Total Price/sqmt\n"
          "(5) Apartment Age\n"
          "(9) select a parameter (column) from database\n")

    string = "Select an variable for the " + axis_type + ":\n"

    while True:
        try:
            x = input(string)
            x = int(x)
            if x - 1 in range(len(axis_list)):
                axis = axis_list[x - 1]
                break

            elif x == 9:
                columns = list(enumerate(columns))
            for num, column in columns:
                print("(" + str(num) + ")", column)

            axis = columns[int(input("Select a parameter:\n"))][1]
            # axis = columns[x]
            break
        except (TypeError, ValueError):
            continue

    print(axis)

    return axis


def apartment_search():
    pass
