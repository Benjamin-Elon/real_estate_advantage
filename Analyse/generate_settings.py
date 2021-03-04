import pandas as pd
from collections import defaultdict

from Analyse import plotting_functions

int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'rooms', 'floor', 'building_floors', 'days_on_market',
                     'days_until_available', 'days_ago_updated']

quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

bool_columns = ['ac', 'b_shelter',
                'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                'long_term', 'pandora_doors']

# date_range_columns = ['date_added', 'updated_at']


def set_locales(con):
    """
    Users select from two scopes. Any more is confusing. I'm working on a better system.
    Makes no sense to compare a scale to a totally different scale.
    Returns: area_selection
    """
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


# TODO: finish this (low priority)
def menu_columns(lst):
    """breaks long lists of locales into printable columns"""
    if len(lst) < 80:
        lst = plotting_functions.chunks(lst, 20)
    elif len(lst) > 80:
        lst = plotting_functions.chunks(lst, len(lst) / 4)
    return lst


def area_menu_select(area_names):
    """
    area_names: [area_name, area_id]
    Generates a list of locales to be selected
    Returns: area_selection
    """
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
    """
    User sets constraints on listings.
    Returns: constraints: {{'toss_outliers': {column: quantile_range},...,
                          {'bool': {column: value},...,
                          {'range': {column: value_range}}'

    NOTE: When fetching listings in apartment_search, only columns with constraints will be displayed"""

    # print("Note: When fetching listings in apartment_search, only columns with constraints will be displayed.")

    constraints = defaultdict()
    constraints = set_outliers(constraints)
    constraints = set_bool(constraints)
    constraints = set_numeric_range(constraints)
    constraints = set_categorical(constraints)
    print("Constraints set:\n", constraints.items())
    return constraints


def set_outliers(constraints):
    """Set thresholds for tossing outliers"""
    while True:
        x = input("Toss outliers [by locale] (y/n)\n"
                  "(2) Auto Toss\n")
        count = 1
        # set outliers for each continuous variable
        if x == 'y':
            constraints['toss_outliers'] = {}
            print("(examples: 3-97, 0-95)\n"
                  "Press enter for to pass\n")
            for column in quantile_columns:
                print("(" + str(count) + "/" + str(len(quantile_columns)) + ")")
                while True:
                    quantiles = input("Quantile range for " + column + ":\n")

                    if quantiles == '':
                        constraints['toss_outliers'][column] = None
                    else:
                        q_low, q_high = set_range(quantiles, column)
                        constraints['toss_outliers'][column] = [float(q_low) * .01, float(q_high) * .01]
                    break
                count += 1
        # automatically set outliers
        elif x == '2':
            constraints['toss_outliers'] = {'price': [0.01, .995], 'price_per_sqmt': [0.01, .99],
                                            'sqmt': [0.005, .985], 'est_arnona': [.015, .99]}
            break
        elif x == 'n':
            constraints['toss_outliers'] = None
        else:
            print('Invalid input...')
            continue
        break

    return constraints


def set_bool(constraints):
    """Set inclusion or exclusion of bool params"""
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
            pass
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
            x = input("Must have " + column + "?) (y/n) (Enter: Pass)\n")
            if x == 'y':
                constraints['bool'][column] = 1
            elif x == 'n':
                constraints['bool'][column] = 0
            elif x == '':
                pass
            else:
                print("Invalid input")
                continue
            count += 1
            break

    if len(constraints['bool']) == 0:
        constraints['bool'] = None

    return constraints


# TODO: write this
def set_categorical(constraints):
    """User selects categorical variables for to include (apartment type, state)"""
    categorical_columns = {'apt_type': ['דירה', 'יחידת דיור', 'גג/פנטהאוז', 'סטודיו/לופט', 'דירת גן', "פרטי/קוטג'",
                                        'סאבלט', 'דופלקס', 'מרתף/פרטר', 'טריפלקס', 'דו משפחתי', 'מחסן', 'דירת נופש',
                                        'חניה', 'כללי', 'משק עזר', 'בניין מגורים', 'משק חקלאי/נחלה', 'מגרשים',
                                        'דיור מוגן'],
                           'apartment_state': ['חדש (גרו בנכס)', 'במצב שמור' 'משופץ', 'חדש מקבלן (לא גרו בנכס)',
                                               'דרוש שיפוץ']}
    # categorical_columns = ['apt_type', 'apartment_state']
    constraints['categorical'] = {}
    while True:
        x = input("Select categorical variables to include? (y/n)\n")
        if x == 'y':
            break
        elif x == 'n':
            constraints['categorical'] = None
            return constraints
        else:
            print("Invalid input...")

    # for each column
    for col, cats in categorical_columns.items():
        col_name = col.replace('_', ' ')
        cat_list = list(enumerate(cats))
        while True:
            x = input("(1) Select categories for: [" + col_name + "]\n"
                      "(2) Auto-select categories\n"
                      "(3) Pass\n")

            # manually select categories
            if x == '1':
                # print the menu
                for num, cat in cat_list:
                    print(cat, '(' + str(num) + ')')

                print('Select categories to include for ' + col_name + ':\n')
                # select categories until finished
                cat_selection = []
                while True:
                    n = input("Make selection ('Enter' : break):\n")
                    if n == '':
                        break
                    try:
                        n = int(n)
                        if cats[n] in cat_selection:
                            print("Already selected...")
                        else:
                            cat_selection.append(cats[n])
                    except (TypeError, KeyError, IndexError, ValueError):
                        print('Invalid input...')

                constraints['categorical'][col] = cat_selection
                break
            # auto select categories
            if x == '2':
                if col == 'apt_type':
                    constraints['categorical'][col] = ['דירה', 'יחידת דיור', 'דירת גן', "פרטי/קוטג'", 'גג/פנטהאוז']
                elif col == 'apartment_state':
                    constraints['categorical'][col] = ['משופץ', 'במצב שמור', 'חדש (גרו בנכס)',
                                                       'חדש מקבלן (לא גרו בנכס)', 'דרוש שיפוץ']
                break
            # pass
            elif x == '3':
                constraints['categorical'][col] = None
                break
            else:
                print("Invalid input...")
                continue

    return constraints


def set_numeric_range(constraints):
    """Set continuous variable constraints"""
    count = 0
    while True:
        x = input("Set numeric range constraints? (y/n)\n"
                  "(1) Auto constrain\n")
        if x == 'y':
            break
        elif x == 'n':
            constraints['range'] = None
            return constraints
        elif x == '1':
            constraints['range'] = {'price': [1000, 10000], 'arnona': [100, 1300], 'sqmt': [13, 350],
                                    'vaad_bayit': [15, 1200], 'days_on_market': [0, 200],
                                    'days_until_available': [0, 150]}
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
            elif int_range == '':
                pass
            break
        count += 1

    return constraints


def set_range(range_str, column):
    """
    Takes in string in format: [ 'int_low-int_high' ]
    Returns: [low, high]
    """
    while True:
        try:
            low, high = range_str.split('-')
            int(low), int(high)
            break
        except (ValueError, TypeError):
            print('invalid input')
            range_str = input("set valid range for " + column + ":\n")

    return int(low), int(high)
