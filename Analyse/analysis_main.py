import pandas as pd
import sqlite3
from collections import OrderedDict
import Analyse.plotting_functions as analysis_functions
import Settings.settings_manager as settings_manager
import Analyse.shape_data as shape_data
import Analyse.generate_settings as generate_settings

con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

# TODO: nefesh bnefesh
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter

int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
                     'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available', 'days_ago_updated']

quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

date_range_columns = ['date_added', 'updated_at']

bool_columns = ['realtor_name', 'ac', 'b_shelter', 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking', 'pets',
                'window_bars', 'elevator', 'sub_apartment', 'renovated', 'long_term', 'pandora_doors',
                'furniture_description', 'description']

categorical_columns = ['apt_type', 'apartment_state']


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
                    df = shape_data.apply_constraints(df, settings['constraints'])
                    break
                elif x == 'n':
                    settings['constraints'] = None
                    break
                else:
                    print("Invalid input...")
                    continue

            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['area_settings'])
            select_analysis(settings['constraints'], listings, upper_name_column, lower_name_column)

            x = input("Would you like to save the current areas and constraints? (y/n)\n")
            if x == 'y':
                settings_manager.save_settings(settings, 'analysis_settings')

        # load settings
        elif x == '2':
            settings = settings_manager.load_settings('analysis_settings')
            if settings is None:
                continue

            # add composite variables and clean up listings
            df = pd.read_sql('SELECT * FROM Listings', con)
            df = shape_data.update_composite_params(df)
            df = shape_data.clean_listings(df)

            # apply constraints - if any
            df = shape_data.apply_constraints(df, settings['constraints'])

            con_1 = sqlite3.connect('yad2_verify_settings.sqlite')
            df.to_sql('yad2_verify_settings.sqlite', con_1)
            con_1.commit()
            con_1.close()

            # get listings from db for each selected area
            listings, upper_name_column, lower_name_column = shape_data.get_listings(df, settings['area_settings'])

            select_analysis(settings['constraints'], listings, upper_name_column, lower_name_column)

        elif x == '3':
            shape_data.update_locales_avgs()

        elif x == '9':
            return

        else:
            print("invalid input")
            continue

    top_menu()


def format_up_down(listings, upper_name_column, lower_name_column, x_axis=None, y_axis=None):
    """
    Return listings as single grouped dataframe of upper areas, or a dict ({upper_area: grouped_df, ...}
    Sorts the dataframes and filters out low sample sizes
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
        df_1 = pd.DataFrame()
        # append all lower areas into single df
        for upper_area_name, df in listings.items():
            # filter by sample threshold for each upper area
            if len(df) > threshold:
                # print(df['price_per_sqmt'].max(), upper_area_name)
                df_1 = df_1.append(df)
            else:
                continue

        # sort by sort_type
        df_1 = shape_data.sort_areas(df_1, sort_type, upper_name_column, x_axis)
        listings = df_1.groupby(upper_name_column, sort=False)
        return listings, option

    elif option == 'down':
        listings_1 = OrderedDict()
        # for each upper area:
        for upper_area, df in listings.items():
            # print(df['price_per_sqmt'].max(), upper_area)
            # group by lower area and filter out low sample sizes
            df = df.groupby(lower_name_column).filter(lambda g: len(g[x_axis].notna()) > threshold)
            # sort by sort_type
            df = shape_data.sort_areas(df, sort_type, lower_name_column, x_axis)
            df_grouped = df.groupby(lower_name_column, sort=False)

            listings_1[upper_area] = df_grouped

        return listings_1, option


def select_analysis(constraints, listings, upper_name_column, lower_name_column):
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
                  "(1) Histogram w/o kde\n"
                  "(2) Histogram w/ kde)\n"
                  "(3) Scatter plot\n"
                  "(4) Ridge plot\n"
                  "(5) Basic data exploration\n"
                  "(9) Back to menu\n")

        # histogram
        if x == '1':
            x_axis = select_axis('distribution')
            listings_1, option = format_up_down(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.display_hists(listings_1, x_axis, option, upper_name_column, lower_name_column)
        # histogram with kde
        elif x == '2':
            x_axis = select_axis('distribution')
            listings_1, option = format_up_down(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.display_hists(listings_1, x_axis, option, upper_name_column, lower_name_column,
                                             kde=True)
        # scatter plot
        elif x == '3':
            x_axis = select_axis('x-axis', rel_plot=True)
            y_axis = select_axis('y-axis', rel_plot=True)
            listings_1, option = format_up_down(listings, upper_name_column, lower_name_column, x_axis)
            settings_manager.save_listings_test(listings_1)
            analysis_functions.display_scatter_plots(listings_1, x_axis, y_axis, option, upper_name_column,
                                                     lower_name_column)
        # ridge plot
        elif x == '4':
            x_axis = select_axis('x-axis')
            listings_1, option = format_up_down(listings, upper_name_column, lower_name_column, x_axis)
            analysis_functions.ridge_plot(listings_1, x_axis, option, upper_name_column, lower_name_column)
        # histograms with 9 variables per area
        # TODO: fix no sort
        elif x == '5':
            listings_1, option = format_up_down(listings, upper_name_column, lower_name_column)
            analysis_functions.explore_data(listings_1, option, upper_name_column, lower_name_column)

        elif x == '9':
            return

        else:
            print("Invalid selection...")
            continue


def select_axis(axis_type, rel_plot=None):

    comp_columns = ['total_price', 'total_price_per_sqmt', 'arnona_per_sqmt', 'price_per_sqmt', 'days_on_market']
    orig_columns = ['price', 'apt_type', 'apartment_state', 'balconies', 'sqmt',
                    'rooms', 'latitude', 'longitude', 'floor', 'ac', 'b_shelter',
                    'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                    'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                    'long_term', 'pandora_doors', 'roommates', 'building_floors',
                    'vaad_bayit', 'arnona']

    if rel_plot is True:
        x = 0
        for column in orig_columns:
            print("(" + str(x) + ")", column)
            x += 1
        string = "Select an variable for the " + axis_type + ":\n"
        while True:
            try:
                x = int(input(string))
                if x in range(len(orig_columns)):
                    axis = orig_columns[x]
                    break
                else:
                    raise ValueError
            except (TypeError, ValueError):
                print("Invalid selection...")
                continue

    else:
        print("(1) Total Price(price + arnona + vaad_bayit)\n"
              "(2) Total Price/sqmt\n"
              "(3) Arnona/sqmt\n"
              "(4) Price/sqmt\n"
              "(5) Apartment Age\n"
              "(9) select a parameter (column) from database\n")

        string = "Select an variable for the " + axis_type + ":\n"
        while True:
            try:
                x = int(input(string))
                x = x - 1
                if x in range(len(comp_columns)):
                    axis = comp_columns[x]
                    break

                elif x == 9:
                    orig_columns = list(enumerate(orig_columns))
                for num, column in orig_columns:
                    print("(" + str(num) + ")", column)

                axis = orig_columns[int(input("Select a parameter:\n"))][1]
                break
            except (TypeError, ValueError):
                print("Invalid selection...")
                continue

    print(axis)

    return axis
