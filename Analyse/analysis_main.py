import pandas as pd
import sqlite3

import Analyse.apartment_search as apartment_search
import Analyse.analysis_functions as analysis_functions
import Settings.settings_manager as settings_manager
import Analyse.shape_data as shape_data

con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

# TODO: nefesh bnefesh
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter

int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
                     'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available']

quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

date_range_columns = ['date_added', 'updated_at']

bool_columns = ['ac', 'b_shelter', 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking', 'pets',
                'window_bars', 'elevator', 'sub_apartment', 'renovated', 'long_term', 'pandora_doors',
                'furniture_description', 'description']

option_columns = ['apt_type', 'apartment_state']


def top_menu():
    # add all the extra variables first
    df = pd.read_sql('SELECT * FROM Listings', con)
    df = shape_data.update_composite_params(df)
    df = shape_data.infer_neighborhood(df)
    df = shape_data.infer_missing_values(df)

    while True:
        x = input("Select action:\n"
                  "(1) Create analysis settings\n"
                  "(2) load analysis settings\n"
                  "(3) Update locale values\n"
                  "(9) Return to main menu\n")

        # create settings
        if x == '1':
            settings = {}
            # select desired locales
            settings['area_settings'] = set_locales()

            while True:
                x = input("Set constraints? (y/n)\n")

                if x == 'y':
                    # set and apply constraints
                    settings['constraints'] = set_constraints()
                    df = shape_data.apply_constraints(df, settings['constraints'])
                    break
                elif x == 'n':
                    settings['constraints'] = None
                    break
                else:
                    print("Invalid input...")
                    continue

            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['area_settings'])
            analysis_menu(settings['constraints'], listings, upper_name_column, lower_name_column)

            x = input("Would you like to save the current areas and constraints? (y/n)\n")
            if x == 'y':
                settings_manager.save_settings(settings, 'analysis_settings')

        # load settings
        elif x == '2':
            settings = settings_manager.load_settings('analysis_settings')
            if settings is None:
                continue
            # apply constraints if any
            df = shape_data.apply_constraints(df, settings['constraints'])
            # get listings from db for each selected area
            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['area_settings'])

            # settings_manager.save_listings_test(listings)

            analysis_menu(settings['constraints'], listings, upper_name_column, lower_name_column)

        elif x == '3':
            shape_data.update_locales_avgs()

        elif x == '9':
            return

        else:
            print("invalid input")
            continue

    top_menu()


def set_locales():
    """Users can select two tiers of areas. Any more is confusing for everyone.
    Makes no sense to compare a scale to a totally different scale."""

    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con).sort_values('top_area_name')
    df_areas = pd.read_sql('SELECT * FROM Areas', con).sort_values('area_name')
    df_cities = pd.read_sql('SELECT * FROM Cities', con).sort_values('city_name')
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con).sort_values('neighborhood_name')
    df_streets = pd.read_sql('SELECT * FROM Streets', con).sort_values('street_name')

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

    while True:
        x = input("Select the largest scale you would like to compare:\n")
        try:
            scopes = scopes[int(x):int(x) + 2]
            break
        except ValueError:
            print("Invalid input...")

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
        for column in quantile_columns:
            print("(" + str(count) + "/" + str(len(quantile_columns)) + ")")
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


def sort_areas(df, sort_type, scope_name_column, x_axis=None, y_axis=None):
    """sorts a dataframe according to selected sort"""

    if sort_type == 'alphabetical':
        df.sort_values(by=scope_name_column, ascending=False)
    elif sort_type == 'x_axis':
        df['area_median'] = df.groupby([scope_name_column])[x_axis].transform('median')
        df = df.sort_values(by='area_median')

    return df


def format_up_down(listings, upper_name_column, lower_name_column, option, x_axis=None, y_axis=None):
    """
    Return listings as single grouped dataframe of upper areas, or a dict ({upper_area: grouped_df, ...}
    Sorts the dataframes and filters out low sample sizes
    """

    # filter areas according to sample threshold (default = 30)
    while True:
        try:
            threshold = input("Set minimum number of listings for inclusion: (default = 30)\n")
            if threshold == '':
                threshold = 30
                break
            else:
                threshold = int(threshold)
            break
        except ValueError:
            print("Invalid input...")

    while True:
        x = input("Set sort type:\n"
                  "(1) Alphabetical (area name)\n"
                  "(2) Numerical (x_axis: median value)\n")
        if x == '1':
            sort_type = 'alphabetical'
            break
        elif x == '2':
            sort_type = 'numerical'
            break
        else:
            print('Invalid selection...')

    if option == 'up':
        df_1 = pd.DataFrame()
        # append all lower areas into single df
        for upper_area_name, df in listings.items():
            # filter by sample threshold for each upper area
            if len(df) > threshold:
                df_1 = df_1.append(df)
            else:
                continue

        # sort by sort_type
        df_1 = sort_areas(df_1, sort_type, upper_name_column, x_axis)
        listings = df_1.groupby(upper_name_column)

    elif option == 'down':
        listings_1 = {}
        # for each upper area:
        for upper_area, df in listings.items():
            # sort by sort_type
            df = sort_areas(df, sort_type, lower_name_column, x_axis)
            # group by lower area and filter out low sample sizes
            df_grouped = df.groupby(lower_name_column).filter(lambda g: len(g) > threshold)
            df_grouped = df_grouped.groupby(lower_name_column)

            listings_1[upper_area] = df_grouped
            listings = listings_1

    return listings


def analysis_menu(constraints, listings, upper_name_column, lower_name_column):
    # while True:
    #     x = input("Select analysis type:\n"
    #               "(1) Apartment search\n"
    #               "(2) Visualization\n"
    #               "(9) Back to menu\n")
    #
    #     if x == '1':
    #         apartment_search.top_menu(constraints, listings, upper_name_column, lower_name_column)
    #
    #     elif x == '2':
    while True:

        while True:
            str1 = ' '
            x = input("Visualize the:\n"
                      "(1) Upper scope (" + str1.join(upper_name_column.split('_')[:-1]) + ")\n OR \n"
                      "(2) Lower scope (" + str1.join(lower_name_column.split('_')[:-1]) + ")\n")
            if x == '1':
                option = 'up'
                break
            elif x == '2':
                option = 'down'
                break
            else:
                print('Invalid selection...')

        x = input("Select visualization type:\n"
                  "(1) Histogram w/o kde\n"
                  "(2) Histogram w/ kde)\n"
                  "(3) Scatter plot\n"
                  "(4) Ridge plot\n"
                  "(5) Basic data exploration\n"
                  "(9) Back to menu\n")

        # histogram
        if x == '1':
            x_axis = select_axis('distribution')
            listings_1 = format_up_down(listings, upper_name_column, lower_name_column, option, x_axis)
            analysis_functions.display_hists(listings_1, x_axis, option, upper_name_column, lower_name_column)
        # histogram with kde
        elif x == '2':
            x_axis = select_axis('distribution')
            listings_1 = format_up_down(listings, upper_name_column, lower_name_column, option, x_axis)
            analysis_functions.display_hists(listings_1, x_axis, option, upper_name_column, lower_name_column,
                                             kde=True)
        # scatter plot
        elif x == '3':
            x_axis = select_axis('x-axis')
            y_axis = select_axis('y-axis')
            listings_1 = format_up_down(listings, upper_name_column, lower_name_column, option, x_axis)
            analysis_functions.display_scatter_plots(listings_1, x_axis, y_axis, option, upper_name_column,
                                                     lower_name_column)
        # ridge plot
        elif x == '4':
            x_axis = select_axis('x-axis')
            listings_1 = format_up_down(listings, upper_name_column, lower_name_column, option, x_axis)
            analysis_functions.ridge_plot(listings_1, x_axis, option, upper_name_column, lower_name_column)
        # histograms with 9 variables per area
        # TODO: fix no sort
        elif x == '5':
            listings_1 = format_up_down(listings, upper_name_column, lower_name_column, option)
            analysis_functions.explore_data(listings_1, option, upper_name_column, lower_name_column)

        elif x == '9':
            return

        else:
            print("Invalid selection...")
            continue


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
            break
        except (TypeError, ValueError):
            print("Invalid selection...")
            continue

    print(axis)

    return axis
