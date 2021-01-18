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


# def sql_to_dataframe():
#     df_dict = {}
#     df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
#     df_areas = pd.read_sql('SELECT * FROM Areas', con)
#     df_cities = pd.read_sql('SELECT * FROM Cities', con)
#     df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
#     return df


def location_settings():
    # df = sql_to_dataframe()
    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
    df_areas = pd.read_sql('SELECT * FROM Areas', con)
    df_cities = pd.read_sql('SELECT * FROM Cities', con)
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con)
    df_streets = pd.read_sql('SELECT * FROM Streets', con)
    settings = {}
    # {{name: [name_column, id_column, identifying_column scope_df]},...}
    scopes = {'top_area': ['top_area_name', 'top_area_id', 'top_area_id', df_top_areas],
              'area': ['area_name', 'area_id', 'top_area_id', df_areas],
              'city': ['city_name', 'city_id', 'area_id', df_cities],
              'neighborhood': ['neighborhood_name', 'neighborhood_id', 'city_id', df_neighborhoods],
              'street': ['street_name', 'street_id', 'city_id', df_streets]}
    scope_names = ['top_area', 'area', 'city', 'neighborhood', 'street']

    num = 0
    for name in scope_names:
        print('(' + str(num) + ')', name)
        num += 1
    # for num, name in enumerate(scopes.keys()):
    #     print('(' + str(num) + ')', name)
    x = input("Select the scale you would like to compare:\n")
    # select scope and the one above
    scope_names = scope_names[int(x)-1:int(x) + 1]

    # values = list(scopes[1])
    # print(values[0])

    id_dict = {}

    scope_name = scope_names[0]
    name_column, id_column, prev_id_column, df = scopes[scope_name]
    id_dict[scope_name] = {}
    # select desired number of areas for scope
    area_names = list(df[name_column])
    menu = list(enumerate(area_names))
    area_ids = select_areas(menu, df, name_column, id_column)
    for area_id in area_ids:
        id_dict[scope_name][area_id] = {}
    for key, value in id_dict[scope_name].items():
        print(key, value)

    # for each selected area, assign sub_areas
    scope_name_1 = scope_names[1]
    print(scope_name_1)
    name_column_1, id_column_1, prev_id_column, df_1 = scopes[scope_name_1]
    for key, value in id_dict[scope_name].items():

        # select area_names for each id
        area_names_1 = list(df_1.loc[df_1[prev_id_column] == key, name_column_1])
        menu = list(enumerate(area_names_1))
        sub_area_ids = select_areas(menu, df_1, name_column_1, id_column_1)
        for area_id in area_ids:
            for sub_area_id in sub_area_ids:
                id_dict[scope_name][area_id] = sub_area_id

    # print(id_dict)


def select_areas(menu, df, prev_id_column, id_column):
    area_selection = []
    area_ids = []

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

    # for each  selected area, get the area_id
    for area in area_selection:
        area_id = int(df.loc[df[prev_id_column] == area, id_column])
        print(area_id)
        area_ids.append(area_id)

    return area_ids


location_settings()


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
