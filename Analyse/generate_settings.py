import pandas as pd
from collections import defaultdict


int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
                     'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available', 'days_ago_updated']

quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

date_range_columns = ['date_added', 'updated_at']

bool_columns = ['realtor', 'ac', 'b_shelter', 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking', 'pets',
                'window_bars', 'elevator', 'sub_apartment', 'renovated', 'long_term', 'pandora_doors',
                'furniture_description', 'description']

categorical_columns = ['apt_type', 'apartment_state']


def set_locales(con):
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
    # TODO: make this nicer (half_done in scratches)
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
                print("invalid selection...")
            else:
                area_name = area_names[x][1][0]
                area_id = area_names[x][1][1]

                if area_name in area_selection:
                    print("already selected...")
                else:
                    area_selection.append([area_id, area_name])

    return area_selection


def set_constraints():
    """User sets constraints on listings.
    Returns constraints: {{'toss_outliers': {column: quantile_range},...,
                          {'bool': {column: value},...,
                          {'range': {column: value_range}}'

    When fetching listings in apartment_search, only columns with constraints will be displayed"""

    # print("Note: When fetching listings in apartment_search, only columns with constraints will be displayed.")

    constraints = defaultdict()
    constraints = set_outliers(constraints)
    constraints = set_bool(constraints)
    constraints = set_numeric_range(constraints)
    print("Constraints set:\n", constraints.items())
    return constraints


def set_outliers(constraints):
    while True:
        x = input("Toss outliers [by locale] (y/n)\n"
                  "(2) Auto Toss\n")
        count = 1
        # set outliers for each continuous variable
        if x == '1':
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
                        constraints['toss_outliers'][column] = [float(q_low)*.01, float(q_high)*.01]
                    break
                count += 1
        # automatically set outliers
        elif x == '2':
            constraints['auto_toss'] = True
            constraints['toss_outliers'] = {'price': [0.01, .995], 'price_per_sqmt': [0.01, .99],
                                            'sqmt': [0.05, .985], 'est_arnona': [.015, .99]}
            break
        elif x == '3':
            constraints['toss_outliers'] = None
        else:
            print('Invalid input...')
            continue
        break

    return constraints


def set_bool(constraints):
    while True:
        x = input("Set bool columns? (y/n)\n")
        if x == 'y':
            break
        elif x == 'n':
            constraints['bool'] = None
            return constraints
        else:
            print("invalid selection...")
            continue

    constraints['bool'] = {}
    # set roommates
    while True:
        x = input("(N/y) Include roommates [note: Inclusion may muddle the data]\n"
                  "(0) Pass\n")
        if x == 'y':
            constraints['bool']['roommates'] = 1
        elif x == 'n' or x == 'N':
            constraints['bool']['roommates'] = 0
        elif x == '0':
            constraints['bool']['roommates'] = None
        else:
            print("Invalid input")
            continue
        break

    # set other bool columns
    count = 1
    constraints['bool'] = {}
    for column in bool_columns:
        while True:
            print("(" + str(count) + "/" + str(len(bool_columns)) + "")
            x = input("Must have " + column + "?) (y/n) (Enter: Pass) (1: Break)\n")
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

    return constraints

def set_categorical():

    return


def set_numeric_range(constraints):
    count = 0
    while True:
        x = input("Set numeric range constraints? (y/n)\n")
        if x == 'y':
            break
        elif x == 'n':
            constraints['range'] = None
            return constraints
        else:
            print("Invalid_input")
            continue

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

    return constraints


def set_range(range_str, column):
    """Takes in string in format 'int-int' -> returns int(low) int(high)"""
    while True:
        try:
            low, high = range_str.split('-')
            int(low), int(high)
            break
        except (ValueError, TypeError):
            print('invalid input')
            range_str = input("set valid range for " + column + ":\n")

    return int(low), int(high)