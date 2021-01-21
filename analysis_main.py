import pandas as pd
import sqlite3
from collections import defaultdict

import analysis_functions
import settings

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
    x = input("Select action:\n"
              "(1) Create analysis settings\n"
              "(2) load analysis settings\n")
    if x == '1':
        scope_ids = location_settings()
        listings, upper_name_column, lower_name_column = get_listings(scope_ids)
        select_analysis_type(listings, upper_name_column, lower_name_column)
    # TODO: write load and save settings functions
    if x == '2':
        settings.load_settings(listings)


def get_listings(area_selection):
    """Uses selected areas to fetch listings from database"""

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']], [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130, 'אזור']]]]


    listings = {}
    df = pd.read_sql('SELECT * FROM Listings', con)
    df = analysis_functions.generate_composite_params(df)

    upper_scope_name, lower_scope_name = area_selection[0]
    upper_id_column = scope_names[upper_scope_name][0]
    lower_id_column = scope_names[lower_scope_name][0]
    upper_name_column = scope_names[upper_scope_name][1]
    lower_name_column = scope_names[lower_scope_name][1]

    area_selection = area_selection[1:]

    for upper_area, lower_areas in zip(area_selection[0], area_selection[1]):
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
        apartment_search()

    elif x == '2':

        x = input("Visualize:\n"
                  "(1) Upper scope (not done)\n"
                  "(2) Lower scope\n")

        option = ['up', 'down']
        option = option[int(x)-1]

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
            analysis_functions.display_scatter_plots(listings, x_axis, y_axis, option, upper_name_column, lower_name_column)


def select_axis(axis_type):

    x = int(input("Select an variable for the " + axis_type + ":\n"
                  "(1) Total Price(price + arnona + vaad_bayit)\n"
                  "(2) Arnona/sqmt\n"
                  "(3) Price/sqmt\n"
                  "(4) Total Price/sqmt\n"
                  "(5) Apartment Age\n"
                  "(9) select a parameter (column) from database\n"))

    axis_list = ['total_price', 'arnona_per_sqmt', 'price_per_sqmt', 'total_price_per_sqmt', 'days_on_market']
    if x-1 in range(len(axis_list)):
        axis = axis_list[x-1]

    elif x == '9':
        for num, column in enumerate(columns):
            print("(" + str(num) + ")", column)

        axis = columns[int(input("Select a parameter:\n"))]

    print(axis)

    return axis


def apartment_search():
    pass


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
    scopes = scopes[int(x):int(x)+2]

    area_ids = []
    area_selection = []
    area_selection.append([scope_names[int(x)], scope_names[int(x) + 1]])

    for scope_name, df in scopes:
        name_column, id_column, prev_id_column = scope_columns[scope_name]
        print(name_column, id_column, prev_id_column)

        if area_ids:
            lower_ids = []
            # for each selected upper area
            for area_id, area_name in area_ids:
                # filter df for areas in upper area
                df_1 = df[df[prev_id_column] == area_id]
                area_names = list(zip(df_1[name_column], df_1[id_column]))
                area_ids = menu_select(area_names)
                lower_ids.append(area_ids)

            area_selection.append(lower_ids)
        else:
            # select upper area ids
            area_names = list(zip(df[name_column], df[id_column]))
            area_ids = menu_select(area_names)
            area_selection.append(area_ids)

    return area_selection


def menu_select(area_names):
    area_selection = []
    area_names = list(enumerate(area_names))
    for num, [area_name, area_id] in area_names:
         print(area_name, '(' + str(num) + ')')

    print("Select desired areas:\n"
          "When finished, press enter or just enter for all areas")
    area_ids = []
    while True:

        x = input()

        if x == '' and area_ids == []:
            for num, [area_name, area_id] in area_names:
                area_ids.append([area_id, area_name])
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
                    area_ids.append([area_id, area_name])

    return area_ids


