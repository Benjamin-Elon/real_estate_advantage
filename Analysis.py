# import numpy as np
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

        # Select as many areas as you want
        while True:
            try:
                x = int(input())
                selection = menu[x]
            except (KeyError, ValueError):
                if x == '':
                    break
                else:
                    print("invalid selection")
            else:
                if x in settings[scope]:
                    print("already selected")
                else:
                    settings[scope].append(x[1])

            # all analysis use a uniform scale throughout. If at any scale, more than one area is selected, it is the last one.
            #  examples:
            #  north -> (haifa, tiberias)
            # north -> haifa -> (neveh shaanan, hadar, carmel)
            # (north, golan, center)
            if len(settings[scope]) > 1:
                break

        # select listings within the geographic selection
        df = df[df[scope].isin(settings[scope])]
        print(df.describe)
    print(df.head)
    print(settings.items())

    return df


df_1 = sql_to_dataframe()
df_1 = select_locations(df_1)
