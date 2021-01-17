# import numpy as np
import pandas as pd
import sqlite3

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

# TODO: impute arnona from average cost per neighborhood
# TODO: derive vaad bayit from other listings in same building
# TODO: Find actual price for roommate listings / filter
# TODO:


# class Locations:
#     def __init__(self):
#         self.top_area_name = []
#         self.area_name = []
#         self.city_name = []
#         self.neighborhood = []
#         self.street = []
#
#     def add_scope(self, scope, *areas):
#         for area in areas:
#             locals()[scope].append(area)


def sql_to_dataframe():
    df = pd.read_sql('SELECT * FROM Listings', con)
    return df


def location_settings():
    df = sql_to_dataframe()
    settings = {}
    scopes = ['area_name', 'city_name', 'neighborhood']
    # for num, name in enumerate(scopes):
    #     print('(' + str(num) + ')', name)
    # x = input("Select the scale you would like to compare:\n")
    # # drop lower scopes
    # scopes = scopes[0:str(x)+1]

    # select areas
    # for each selected area:
    # select sub_areas
    # for each sub_area:
    # select_sub_sub_areas

    # select areas
    area_names = list(df['area_name'].drop_duplicates())
    menu = list(enumerate(area_names))

    area_selection = select_areas(menu)
    for area in area_selection:
        print(area)
        new_df = df[df['area_name'] == area]
        city_names = new_df['city_name'].drop_duplicates()
        menu = list(enumerate(city_names))
        city_selection = select_areas(menu)
        for city in city_selection:
            neighborhood_names = df[(df['neighborhood']) | (df['city_name'] == city)].drop_duplicates()
            menu = list(enumerate(neighborhood_names))
            neighborhood_selection = select_areas(menu)


def select_areas(menu):

    area_selection = []

    # print menu
    for num, name in menu:
        if name != '':
            print(name, '(' + str(num) + ')')

    print("Select desired areas:\n"
          "When finished, press enter or just enter for all areas")

    while True:
        x = input()

        if x == '' and area_selection == []:
            for num, area in menu:
                area_selection.append(area)
        elif x == '':
            break

        # if valid area is selected, add it to the scope list
        else:
            try:
                x = int(x)
            except (ValueError, KeyError):
                print("invalid selection")
            else:
                area = menu[x][1]
                if area in area_selection:
                    print("already selected")
                else:
                    area_selection.append(area)
    print(area_selection)
    return area_selection


# location_settings()


    # area_names = list(df[scope].drop_duplicates())
    # menu = list(enumerate(area_names))
    #
    # # print menu
    # for num, name in menu:
    #     if name != '':
    #         print(name, '(' + str(num) + ')')
    #
    # print("Select desired areas:\n"
    #       "When finished, press enter or just enter for all areas")
    #
    # while True:
    #     x = input()
    #
    #     try:
    #         x = int(x)
    #         area = menu[x]
    #
    #     except (KeyError, ValueError):
    #         if x == '' and settings[area] == []:
    #             for item in menu:
    #                 settings[scope].append(item)
    #             break
    #         elif x == '':
    #             break
    #         else:
    #             print("invalid selection")
    #
    #     # if valid area is selected, add it to the scope list
    #     else:
    #         if x in settings[scope]:
    #             print("already selected")
    #         else:
    #             settings[scope].append(selection)




    # # get menu options for each prior selection
    # for area in scopes[count-1]:
    #     area_names = list(df[area].drop_duplicates())
    #     menu = list(enumerate(area_names))
    #
    #     # print menu
    #     for x, name in menu:
    #         if name != '':
    #             print(name, '(' + str(x) + ')')
    #
    #     print("Select desired areas for:", area, "\n"
    #           "When finished, press enter or just enter for all")
    #
    #     settings[scope][area] = []
    #
    #     # Select as many areas as you want
    #     # all analysis use a uniform scale throughout. Can only compare uniform scales.
    #     #  examples:
    #     #  north -> (haifa, tiberias)
    #     # north -> haifa -> (neveh shaanan, hadar, carmel)
    #     # (north, golan, center)
    #     while True:
    #         x = input()
    #
    #         try:
    #             x = int(x)
    #             selection = menu[x]
    #
    #         except (KeyError, ValueError):
    #             if x == '' and settings[scope] == []:
    #                 for item in menu:
    #                     settings[scope].append(item)
    #                 break
    #             elif x == '':
    #                 break
    #             else:
    #                 print("invalid selection")
    #
    #         # if valid area is selected, add it to the scope list
    #         else:
    #             if x in settings[scope]:
    #                 print("already selected")
    #             else:
    #                 settings[scope].append(selection)
    #
    # # if scope is top_area
    # else:
    #     settings[scope] = []
    #     area_names = list(df[scope].drop_duplicates())
    #     menu = list(enumerate(area_names))
    #
    #     # print menu
    #     for x, name in menu:
    #         if name != '':
    #             print(name, '(' + str(x) + ')')
    #
    #     print("Select desired areas:\n"
    #           "When finished, press enter")
    #
    #     while True:
    #         x = input()
    #
    #         try:
    #             x = int(x)
    #             selection = menu[x]
    #
    #         except (KeyError, ValueError):
    #             if x == '' and settings[scope] == []:
    #                 for item in menu:
    #                     settings[scope].append(item)
    #                 break
    #             elif x == '':
    #                 break
    #             else:
    #                 print("invalid selection")
    #
    #         # if valid area is selected, add it to the scope list
    #         else:
    #             if x in settings[scope]:
    #                 print("already selected")
    #             else:
    #                 settings[scope].append(selection)

    # select listings within the geographic selection
    # df = df[df[scope].isin(settings[scope])]
    # count += 1
    #
    # # print(df.describe)
    # # print(df.head)
    # print(settings.items())
    # print(settings)
    #
    # return df


# df_1 = sql_to_dataframe()
# df_1 = location_settings(df_1)
