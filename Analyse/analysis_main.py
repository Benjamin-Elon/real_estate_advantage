import os
import pandas as pd
import sqlite3
from collections import OrderedDict
import itertools

import Analyse.plotting_functions as analysis_functions
import Settings.settings_manager as settings_manager
import Analyse.apply_settings as shape_data
import Analyse.generate_settings as generate_settings


con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

# TODO: nbn


def top_menu():

    while True:
        x = input("Select action:\n"
                  "(1) Create analysis settings\n"
                  "(2) load analysis settings\n"
                  "(3) Update locale values\n"
                  "(9) Return to main menu\n")

        # create settings
        if x == '1':
            df = pd.read_sql('SELECT * FROM Listings', con)
            # add composite variables and clean up listings
            df = shape_data.update_composite_params(df)
            df = shape_data.clean_listings(df)
            settings = {}
            # select desired locales
            settings['area_settings'] = generate_settings.set_locales(con)

            while True:
                x = input("Set constraints? (y/n)\n")

                if x == 'y':
                    # set and apply constraints
                    settings['constraints'] = generate_settings.set_constraints()
                    if settings['constraints'] is not None:
                        listings, upper_name_column, lower_name_column = shape_data.select_listings(df, settings[
                            'area_settings'])

                        listings = shape_data.apply_constraints(listings, settings['constraints'])
                elif x == 'n':
                    settings['constraints'] = None
                    listings, upper_name_column, lower_name_column = shape_data.select_listings(df, settings[
                        'area_settings'])

                else:
                    print("Invalid input...")
                    continue
                break

            x = input("Would you like to save the current areas and constraints? (y/n)\n")
            if x == 'y':
                settings_manager.save_settings(settings, 'analysis_settings')
            select_analysis(settings['constraints'], listings, upper_name_column, lower_name_column)

        # load settings
        elif x == '2':
            settings = settings_manager.load_settings('analysis_settings')
            if settings is None:
                continue

            # add composite variables and clean up listings
            df = pd.read_sql('SELECT * FROM Listings', con)
            # get listings from db for each selected area
            listings, upper_name_column, lower_name_column = shape_data.select_listings(df, settings['area_settings'])
            listings = shape_data.update_composite_params(listings)
            listings = shape_data.clean_listings(listings)

            # apply constraints - if any
            if settings['constraints'] is not None:

                listings = shape_data.apply_constraints(listings, settings['constraints'])
                # print(settings['constraints'].keys())

            # TODO: remove after done testing
            try:
                os.remove("yad2_verify_settings.sqlite")
            except FileNotFoundError:
                pass
            con_1 = sqlite3.connect('yad2_verify_settings.sqlite')
            df.to_sql('yad2_verify_settings.sqlite', con_1)
            con_1.commit()
            con_1.close()

            select_analysis(settings['constraints'], listings, upper_name_column, lower_name_column)

        elif x == '3':
            shape_data.update_locales_avgs()

        elif x == '9':
            return

        else:
            print("invalid input")
            continue
    settings_manager.save_listings_test(settings, 'settings.pkl')
    top_menu()


def sort_and_filter(listings, upper_name_column, lower_name_column, x_axis=None, y_axis=None):
    """
    Formats the Listings df as single grouped dataframe of upper areas, or a dict ({upper_area: grouped_df, ...}
    Sorts the df and filters out low sample sizes
    Return modified df as listings
    """

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
        # filter out low sample sizes
        listings = listings.groupby(upper_name_column).filter(lambda g: len(g[g[x_axis].notna()]) > threshold)
        # sort upper areas
        listings = shape_data.sort_areas(listings, sort_type, upper_name_column, x_axis)
        return listings, option

    elif option == 'down':
        listings_1 = pd.DataFrame()
        listings = listings.groupby(upper_name_column)

        for upper_area, df in listings:
            # filter out low sample sizes
            df = df.groupby(lower_name_column).filter(lambda g: len(g[x_axis].notna()) > threshold)
            # sort lower areas
            df = shape_data.sort_areas(df, sort_type, lower_name_column, x_axis)

            listings_1 = listings_1.append(df)

        return listings_1, option


def convert_bool_columns(df):
    """Converts 0/1 to yes,no (column) for displaying in the figure legend"""

    bool_columns = ['ac', 'balconies', 'b_shelter', 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                    'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated', 'long_term', 'pandora_doors']
    for col in bool_columns:
        df[col] = df[col].apply(lambda x: "No " + col.replace('_', ' ') if x == 0 else col.replace('_', ' '))
    return df


def select_analysis(constraints, listings, upper_name_column, lower_name_column):
    """User selects the type of visualization and axes for plotting"""
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
        x = input("Select visualization type:\n"
                  "(1) Histogram \n"
                  "(2) Histogram + kde)\n"
                  "(3) Scatter plot\n"
                  "(4) Scatter plot + multiple regression\n"
                  "(4) Ridge plot\n"
                  "(5) Basic data exploration\n"
                  "(9) Back to menu\n")

        listings = convert_bool_columns(listings)
        bool_columns = ['ac', 'b_shelter', 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                        'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated', 'long_term', 'pandora_doors']

        # histogram
        if x == '1':
            x_axis = select_axes(['distribution'])
            listings_1, scope = sort_and_filter(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.display_hists(listings_1, upper_name_column, lower_name_column, x_axis, scope, kde=False)
        # histogram with kde
        elif x == '2':
            x_axis = select_axes(['distribution'])
            listings_1, scope = sort_and_filter(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.display_hists(listings_1, upper_name_column, lower_name_column, x_axis, scope, kde=True)
        # scatter plot
        elif x == '3':
            x_axis, y_axis, hue = select_axes(['x-axis', 'y_axis', 'hue'], rel_plot=True)
            listings_1, scope = sort_and_filter(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.display_scatter_plots(listings_1, upper_name_column, lower_name_column, x_axis, y_axis, scope, hue)
        # multiple regression plot
        elif x == '4':
            x_axis, y_axis, hue = select_axes(['x-axis', 'y_axis', 'hue'], rel_plot=True)
            listings_1, scope = sort_and_filter(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.multiple_lin_reg_plot(listings_1, scope, x_axis, y_axis, hue, upper_name_column, lower_name_column)
        # ridge plot
        elif x == '5':
            x_axis = select_axes('x-axis')
            listings_1, scope = sort_and_filter(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.ridge_plot(listings_1, x_axis, scope, upper_name_column, lower_name_column)
        # quick visualization. histograms with 9 variables per area
        # TODO: fix no sort
        elif x == '6':
            listings_1, option = sort_and_filter(listings, upper_name_column, lower_name_column)
            analysis_functions.explore_data(listings_1, option, upper_name_column, lower_name_column)
        # return to previous menu
        elif x == '9':
            return

        else:
            print("Invalid selection...")
            continue


def select_axes(axes, rel_plot=False):
    """
    User selects variables for plotting from a menu of options sorted in columns by variable type.
    Returns: A list of axes for plotting
    """
    continuous_columns = {0: 'price', 1: 'arnona', 2: 'vaad_bayit', 3: 'sqmt', 4: 'total_price', 5: 'arnona_per_sqmt',
                          6: 'total_price_per_sqmt', 7: 'price_per_sqmt', 8: 'days_on_market',
                          9: 'days_until_available',
                          10: 'days_since_update'}

    bool_columns = {20: 'realtor', 21: 'balconies', 22: 'rooms', 23: 'floor', 24: 'ac', 25: 'b_shelter',
                    26: 'furniture',
                    27: 'central_ac', 28: 'sunroom', 29: 'storage', '': ''}

    bool_columns_1 = {30: 'accesible', 31: 'parking', 32: 'pets', 33: 'window_bars', 34: 'elevator',
                      35: 'sub_apartment', 36: 'renovated',
                      37: 'long_term', 38: 'pandora_doors', 39: 'roommates'}

    estimated_columns = {50: 'est_arnona', 51: 'arnona_ratio', 52: 'est_price', 53: 'est_price', 54: 'price_ratio'}

    categorical_columns = {40: 'apt_type', 41: 'apartment_state', 42: 'building_floors'}
    axis_list = []
    col_dict = {}
    if rel_plot is True:
        # merge all columns into one dictionary for easy selecting
        col_dict.update(continuous_columns)
        col_dict.update(bool_columns)
        col_dict.update(bool_columns_1)
        col_dict.update(categorical_columns)
        col_dict.update(estimated_columns)
        # for each axis in the rel plot
        for axis in axes:
            # print a columns of types of variables
            print(f"{'CONTINUOUS VARS:'} {'BOOL VARS:':>22} {'BOOL VARS:':>24} {'CATEGORICAL VARS':>30} {'INFERRED VARS':>21}")
            for x in itertools.zip_longest(continuous_columns.items(), bool_columns.items(), bool_columns_1.items(),
                                           categorical_columns.items(), estimated_columns.items(), fillvalue=''):
                [n1, col1], [n2, col2], [n3, col3], [n4, col4], [n5, col5] = \
                    ['', ''], ['', ''], ['', ''], ['', ''], ['', '']

                # if 5/5 columns are in row
                try:
                    [n1, col1], [n2, col2], [n3, col3], [n4, col4], [n5, col5] = x
                    string = f"(" + str(n1) + ") {col1:<25}" "(" + str(n2) + ") {col2:<20}" + "(" + str(
                        n3) + ") {col3:<20}" + "(" + str(n4) + ") {col4:<20}" + "(" + str(n5) + ") {col5:<20}"
                    print(string.format(col1=col1, col2=col2, col3=col3, col4=col4, col5=col5))

                except ValueError:
                    # if 3/5 columns are in row
                    if n5 == '' and n4 == '' and n3 == '':
                        string = f"(" + str(n1) + ") {col1:<25}"
                        print(string.format(col1=col1))
                    # if 2/5 columns are in row
                    elif n5 == '' and n4 == '':
                        string = f"(" + str(n1) + ") {col1:<25}" "(" + str(n2) + ") {col2:<20}"
                        print(string.format(col1=col1, col2=col2))
                    # if 1/5 columns are in row
                    elif n5 == '':
                        string = f"(" + str(n1) + ") {col1:<25}" "(" + str(n2) + ") {col2:<20}" + "(" + str(
                            n3) + ") {col3:<20}" + "(" + str(n4) + ") {col3:<20}"
                        print(string.format(col1=col1, col2=col2, col3=col3, col4=col4))

            # select a variable for the current axis
            while True:
                string = "Select an variable for the " + axis + ":\n"
                x = input(string)
                try:
                    selection = col_dict[int(x)]
                    # variables can be used once only
                    if selection in axis_list:
                        print('Already selected...')
                        continue
                except (ValueError, KeyError):
                    print("Invalid selection...")
                    continue
                else:
                    axis_list.append(selection)
                    break

    elif rel_plot is False:
        col_dict.update(continuous_columns)
        col_dict.update(estimated_columns)
        for axis in axes:
            print(f"{'CONTINUOUS VARS:'} {'INFERRED VARS':>21}")
            for x in itertools.zip_longest(continuous_columns.items(), estimated_columns.items(), fillvalue=''):
                [n1, col1], [n2, col2] = ['', ''], ['', '']
                try:
                    [n1, col1], [n2, col2] = x
                    string = f"(" + str(n1) + ") {col1:<25}" "(" + str(n2) + ") {col2:<20}"
                    print(string.format(col1=col1, col2=col2))

                except ValueError:
                    if n2 == '':
                        string = f"(" + str(n1) + ") {col1:<25}"
                        print(string.format(col1=col1))

            while True:
                string = "Select an variable for the " + axis + ":\n"
                x = input(string)
                try:
                    selection = col_dict[int(x)]
                    if selection in axis_list:
                        print('Already selected...')
                        continue
                except (ValueError, KeyError):
                    print("Invalid selection...")
                    continue
                else:
                    axis_list.append(selection)
                    break
        print(list(zip(axes, axis_list)))
    if len(axis_list) == 1:
        axis_list = axis_list[0]

    return axis_list


# def select_axis(axes, rel_plot=None):
#     """select an axis for plotting (x,y ,hue)"""
#     # continuous_columns = ['price', 'arnona', 'vaad_bayit', 'sqmt', 'total_price', 'arnona_per_sqmt',
#     #                       'total_price_per_sqmt',
#     #                       'price_per_sqmt', 'days_on_market', 'days_until_available', 'days_since_update']
#     #
#     # bool_columns = ['realtor', 'balconies', 'rooms', 'floor', 'ac', 'b_shelter', 'furniture', 'central_ac', 'sunroom',
#     #                 'storage', 'accesible', 'parking', 'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
#     #                 'long_term', 'pandora_doors', 'roommates']
#     #
#     # categorical_columns = ['apt_type', 'apartment_state', 'building_floors']
#     #
#     # comp_columns = ['total_price', 'total_price_per_sqmt', 'arnona_per_sqmt', 'price_per_sqmt', 'days_on_market']
#     # orig_columns = ['price', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
#     #                 'rooms', 'latitude', 'longitude', 'floor', 'ac', 'b_shelter',
#     #                 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
#     #                 'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
#     #                 'long_term', 'pandora_doors', 'roommates', 'building_floors',
#     #                 'vaad_bayit', 'arnona']
#
#     # scatter plots, rel plots, ect...
#     # select axes
#     if rel_plot is True:
#         axis_selection = select_axes(axes)
#
#     # distributions, hist, kde, ect
#     else:
#         axis_selection = dist_plot_axis(axes)
#         print("(1) Total Price(price + arnona + vaad_bayit)\n"
#               "(2) Total Price/sqmt\n"
#               "(3) Arnona/sqmt\n"
#               "(4) Price/sqmt\n"
#               "(5) Apartment Age\n"
#               "(9) select a parameter (column) from database\n")
#
#         string = "Select an variable for the " + axis_type + ":\n"
#         while True:
#             try:
#                 x = int(input(string))
#                 x = x - 1
#                 if x in range(len(comp_columns)):
#                     axis = comp_columns[x]
#                     break
#
#                 elif x == 9:
#                     orig_columns = list(enumerate(orig_columns))
#                 for num, column in orig_columns:
#                     print("(" + str(num) + ")", column)
#
#                 axis = orig_columns[int(input("Select a parameter:\n"))][1]
#                 break
#             except (TypeError, ValueError):
#                 print("Invalid selection...")
#                 continue
#
#     print(axis)
#
#     return axis
