import numpy as np
import pandas as pd
import sqlite3

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

settings = {}
# TODO: impute arnona from average cost per neighborhood
# TODO: derive vaad bayit from other listings in same building
# TODO: Find actual price for roommate listings / filter
# TODO:


def sql_to_dataframe():
    df = pd.read_sql('SELECT * FROM Listings', con)
    return df


def select_locations(df):

    scopes = ['top_area_name', 'area_name', 'city_name', 'neighborhood', 'street']
    for scope in scopes:
        area_names = list(df[scope].drop_duplicates())
        menu = list(enumerate(area_names))

        # print menu
        for x, name in menu:
            if name != '':
                print(name, '(' + str(x) + ')')

        print("Select desired areas:\n"
              "When finished, press enter")

        settings[scope] = []
        x = None
        # Select as many areas as you want
        while x is not False:
            try:
                x = input()
                x = menu[int(x)]
            except (KeyError, ValueError):
                if x == '':
                    x = False
                else:
                    print("invalid selection")
            else:
                if x in settings[scope]:
                    print("already selected")
                else:
                    settings[scope].append(x[1])

        # select listings within the geographic selection
        df = df[df[scope].isin(settings[scope])]
        print(df.describe)
    print(df.head)
    print(settings.items())


# df_1 = sql_to_dataframe()
# select_locations(df_1)
