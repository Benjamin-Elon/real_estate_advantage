import pandas as pd
import sqlite3
from collections import defaultdict
import apartment_search
import analysis_functions
import settings_manager
import shape_data

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

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


def top_menu():

    # add all the extra variables first
    df = pd.read_sql('SELECT * FROM Listings', con)
    df = analysis_functions.generate_composite_params(df)

    while True:
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
                df = shape_data.apply_constraints(df, settings['constraints'])
            else:
                settings['constraints'] = None

            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['area_settings'])
            analysis_menu(settings['constraints'], listings, upper_name_column, lower_name_column)

            x = input("Would you like to save the current areas and constraints? (not including stat settings) (y/n)\n")
            if x == 'y':
                settings_manager.save_settings(settings, 'analysis_settings')

        # load settings
        elif x == '2':
            settings = settings_manager.load_settings('area_selection')
            # apply constraints if any
            df = shape_data.apply_constraints(df, settings['constraints'])
            # get listings from db for each selected area
            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['analysis_settings'])
            analysis_menu(settings['constraints'], listings, upper_name_column, lower_name_column)

        elif x == '3':
            shape_data.update_geo_coords()

        elif x == '9':
            return

        else:
            print("invalid input")
            continue

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
            area_selection = area_menu_select(area_names)
            area_settings.append(area_selection)

        else:

            lower_ids = []
            # for each selected upper area
            for area_id, area_name in area_selection:
                print(area_id, area_name)
                # filter df for areas in upper area
                df_1 = df.loc[df[prev_id_column] == area_id]
                area_names = list(zip(df_1[name_column], df_1[id_column]))
                area_ids = area_menu_select(area_names)
                lower_ids.append(area_ids)

            area_settings.append(lower_ids)

    return area_settings


def area_menu_select(area_names):
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


# TODO: set date range constraints. low priority
def set_constraints():
    """User sets constraints on listings.
    Returns constraints: {{'toss_outliers': {column: quantile_range},...,
                          {'bool': {column: value},...,
                          {'range': {column: value_range}}'

    When fetching listings in apartment_search, only columns with constraints will be displayed"""

    print("Note: When fetching listings in apartment_search, only columns with constraints will be displayed.")

    constraints = {}

    x = input("Toss outliers (by locale) (y/n):\n")
    count = 1
    if x == 'y':
        constraints['toss_outliers'] = {}
        print("(examples: 3-97, 0-95)\n"
              "Press enter for 'None'\n")
        for column in int_range_columns:
            print("(" + str(count) + "/" + str(len(int_range_columns)) + ")")
            while True:
                quantiles = input("Quantile range for " + column + ":\n")

                if quantiles == '':
                    constraints['toss_outliers'][column] = None
                else:
                    q_low, q_high = set_range(quantiles, column)
                    constraints['toss_outliers'][column] = [q_low, q_high]
                break
            count += 1

    else:
        constraints['toss_outliers'] = None

    constraints['bool'] = {}
    while True:
        x = input("Include listings with roommates? (y/n, pass:'enter') (not full prices usually)\n")
        if x == 'y':
            constraints['bool']['roommates'] = 1
        elif x == 'n':
            constraints['bool']['roommates'] = 0
        elif x == '':
            constraints['bool']['roommates'] = None
        else:
            print("Invalid input")
            continue
        break

    count = 1
    constraints['bool'] = {}
    for column in bool_columns:
        while True:
            print("(" + str(count) + "/" + str(len(bool_columns)) + ")")
            x = input("Must have " + column + "? (y/n, pass:'enter')\n")
            if x == 'y':
                constraints['bool'][column] = 1
            elif x == 'n':
                constraints['bool'][column] = 0
            elif x == '':
                constraints['bool'][column] = None
            else:
                print("Invalid input")
                continue
            count += 1
            break

    if len(constraints['bool']) == 0:
        constraints['bool'] = None

    count = 0
    x = input("Set numeric range constraints? (y/n)\n")
    if x == 'y':
        constraints['range'] = {}
        for column in int_range_columns:
            print("(" + str(count) + "/" + str(len(int_range_columns)) + ")")
            while True:
                print("(examples: 1000-2500, 0-200, 150-400)")
                int_range = input("Set range for " + column + ":\n")
                if int_range != '':
                    low, high = set_range(int_range, column)
                    constraints['range'][column] = [low, high]
                    break
                elif int_range == '':
                    constraints['range'][column] = None
                    break
            count += 1
    else:
        constraints['range'] = None

    return constraints


def set_range(range_str, column):
    low, high = range_str.split('-')
    while True:
        try:
            int(low), int(high)
            break
        except (ValueError, TypeError):
            print('invalid input')
            range_str = input("set valid range for" + column + ":\n")

            low, high = set_range(range_str, column)

    return int(low), int(high)


def analysis_menu(constraints, listings, upper_name_column, lower_name_column):

    while True:
        x = input("Select analysis type:\n"
                  "(1) Apartment search\n"
                  "(2) Visualization\n"
                  "(9) Back to menu\n")

        if x == '1':
            apartment_search.top_menu(constraints, listings, upper_name_column, lower_name_column)

        elif x == '2':
            str1 = ' '
            x = input("Visualize:\n"
                      "(1) Upper scope (" + str1.join((upper_name_column.split('_')[:-1])) + ")\n"
                      "(2) Lower scope (" + str1.join((lower_name_column.split('_')[:-1])) + ")\n")

            option = ['up', 'down']
            option = option[int(x) - 1]

            while True:
                x = input("Select visualization type:\n"
                          "(1) Distribution(Histogram)\n"
                          "(2) Distribution(kde with rugs)\n"
                          "(3) Scatter plots\n")

                if x == '1':
                    y_axis = select_axis('distribution')
                    analysis_functions.display_hists(listings, y_axis, option, upper_name_column, lower_name_column)
                    break

                elif x == '2':
                    x_axis = select_axis('distribution')
                    analysis_functions.display_distributions(listings, x_axis, option, upper_name_column, lower_name_column)
                    break

                elif x == '3':
                    x_axis = select_axis('x-axis')
                    y_axis = select_axis('y-axis')
                    analysis_functions.display_scatter_plots(listings, x_axis, y_axis, option, upper_name_column,
                                                             lower_name_column)
                    break
                else:
                    print("Invalid selection...")

        elif x == '9':
            return

        else:
            print("Invalid selection...")


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
            print("Invalid selection...")
            continue

    print(axis)

    return axis


def apartment_search():
    pass
