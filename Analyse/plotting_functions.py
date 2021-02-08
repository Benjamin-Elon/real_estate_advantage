from matplotlib import cm
import joypy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math
import sqlite3

# TODO: add sort by (price, alphabetical, top_x ect)
con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

df_listings = pd.read_sql('SELECT * FROM Listings', con)


def display_hists(listings, x_axis, option, upper_name_column, lower_name_column, kde=False):
    # get rid of rows without x_axis values
    df_listings_1 = df_listings[df_listings[x_axis].notna()]
    # get the median value of the x_axis for all listings
    x_axis_med = df_listings_1[x_axis].median()

    if option == 'up':
        areas_chunked = chunks(list(listings.groups), 12)
        for areas in areas_chunked:
            fig, axes = plt.subplots(nrows=4, ncols=3, sharex=True)
            for area, ax in zip(areas, axes.flatten(order='A')):
                df_area = listings.get_group(area)
                sns.histplot(data=df_area, x=x_axis, ax=ax, kde=kde, binwidth=100)
                ax.title.set_text(area[::-1] + ", n = " + str(len(df_area)))
                median = df_area[x_axis].median()
                median = round(median, 1)
                ax.axvline(x=median, ymin=0, color='r', )
                ax.text(median, 2, median, rotation=90)
        plt.tight_layout()
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df_areas in listings.items():
            # split lower areas into chunks
            area_chunks = chunks(list(df_areas.groups), 12)
            # for lower areas chunk
            for area_chunk in area_chunks:
                fig, axes = plt.subplots(nrows=4, ncols=3, sharex=True)
                # plot each lower area as subplot
                for area, ax in zip(area_chunk, axes.flatten(order='F')):
                    # get lower area from grouped_df
                    df = df_areas.get_group(area)
                    bin_width = x_axis_med/(math.log(len(df), 10)*5)
                    # print(x_axis_med, len(df), bin_width)
                    print(area, df[x_axis].max())
                    sns.histplot(data=df, x=x_axis, ax=ax, kde=kde, binwidth=bin_width)
                    ax.title.set_text(area[::-1] + ", n = " + str(len(df)))
                    # place vertical line on each subplot for median value
                    median = df[x_axis].median()
                    median = round(median, 1)
                    ax.axvline(x=median, ymin=0, color='r', )
                    ax.text(median, 2, median, rotation=90)

            # plot all lower areas for each upper area
            plt.suptitle(upper_area_name[::-1])
            plt.tight_layout()
            plt.subplots_adjust(top=1.2)
        plt.show()

    return


def display_scatter_plots(listings, x_axis, y_axis, option, upper_name_column, lower_name_column):
    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        df_1 = reverse_name_values(df_1)
        sns.relplot(data=df_1, x=x_axis, y=y_axis, col=upper_name_column, col_wrap=4)
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df in listings.items():
            # display lower areas as subplots
            df = reverse_name_values(df)
            sns.relplot(data=df, x=x_axis, y=y_axis, col=lower_name_column, col_wrap=4)
            plt.suptitle(upper_area_name[::-1])
            plt.show()


def reverse_name_values(df):
    """Reverse the hebrew name in a dataframe so that they will be displayed properly"""

    df_columns = ['top_area_name', 'area_name', 'city_name', 'neighborhood_name', 'street_name', 'contact_name']

    for column in df_columns:
        value_list = []
        for value in df[column]:
            try:
                value = value[::-1]
                value_list.append(value)
            except TypeError:
                value_list.append(value)

        df[column] = value_list

    return df


def chunks(lst, size):
    """Yield successive sized chunks from lst."""
    for x in range(0, len(lst), size):
        yield lst[x:x + size]


def ridge_plot(listings, x_axis, option, upper_name_column, lower_name_column):
    # filter areas according to sample threshold
    while True:
        try:
            threshold = int(input("Set minimum number of listings for inclusion:\n"))
            break
        except ValueError:
            print("Invalid input...")

    if option == 'up':
        df_1 = pd.DataFrame()
        # combine all lower areas into single df
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        # sort upper areas alphabetically
        df = df_1.sort_values(upper_name_column)
        # group by upper area
        df_grouped = df.groupby(upper_name_column)

        area_names = []
        for area, df_area in df_grouped:
            if len(df_area) > threshold:
                area_names.append(area)

        # sort area names
        area_names = sorted(area_names, reverse=False)
        area_names_1 = []

        # reverse area names in list so they match the reversed dataframe
        for area in area_names:
            area_names_1.append(area[::-1])
        area_names = area_names_1

        # split areas into chunks so the graph isn't cluttered
        area_names = chunks(area_names, 10)

        df = reverse_name_values(df)

        # for chunk: graph areas in chunk
        for chunk in area_names:
            df_chunk = df[df[upper_name_column].isin(chunk)]

            joypy.joyplot(df_chunk, by=upper_name_column, column=x_axis,
                          kind="kde",
                          range_style='own', tails=0.2,
                          overlap=3, linewidth=1, colormap=cm.autumn_r,
                          labels=chunk, grid='y', figsize=(7, 7),
                          title=upper_name_column.replace('_', ' ') + ": " + x_axis)
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df in listings.items():
            # sort upper areas alphabetically
            df = df.sort_values(upper_name_column)
            # group by lower area
            df_grouped = df.groupby(lower_name_column)

            # get list of lower areas in upper area
            area_names = []
            for area, df_area in df_grouped:
                if len(df_area) > threshold:
                    area_names.append(area)

            # sort area names
            area_names = sorted(area_names, reverse=False)
            area_names_1 = []

            # reverse area names in list so they match the reversed dataframe
            for area in area_names:
                area_names_1.append(area[::-1])
            area_names = area_names_1

            # split areas into chunks so the graph isn't cluttered
            area_names = chunks(area_names, 10)

            df = reverse_name_values(df)

            # for chunk: graph areas in chunk
            for chunk in area_names:
                df_chunk = df[df[lower_name_column].isin(chunk)]

                joypy.joyplot(df_chunk, by=lower_name_column, column=x_axis,
                              kind="kde",
                              range_style='own', tails=0.2,
                              overlap=3, linewidth=1, colormap=cm.autumn_r,
                              labels=chunk, grid='y', figsize=(7, 7),
                              title=upper_area_name[::-1].replace('_', ' ') + ": " + x_axis)
            plt.show()


def explore_data(listings, option, upper_name_column, lower_name_column):
    bins_quantiles = {'price': [250, [0.01, .995]], 'price_per_sqmt': [1, [0.01, .99]],
                      'sqmt': [10, [0.05, .985]], 'est_arnona': [50, [.015, .99]], 'rooms': [1, [.0, 1.0]],
                      'floor': [1, [.0, 1.0]], 'building_floors': [1, [.0, 1.0]],
                      'days_on_market': [10, [.01, .98]], 'days_until_available': [10, [.01, .99]]}

    if option == 'up':
        for area, df in listings.items():

            fig, axes = plt.subplots(nrows=3, ncols=3)
            print(area)
            for (column, [bin_width, [q_low, q_high]]), ax in zip(bins_quantiles.items(), axes.flatten()):
                q_low = df[column].quantile(q_low)
                q_high = df[column].quantile(q_high)
                df_2 = df.loc[(df[column] < q_high) & (df[column] > q_low)]

                sns.histplot(df_2[column], x=df_2[column], ax=ax, binwidth=bin_width)

                plt.tight_layout()
                plt.suptitle(area[::-1] + ", n = " + str(len(df)))

        plt.show()

    # TODO: test this
    elif option == 'down':
        # for each upper area
        for upper_area, df_grouped in listings.items():
            # check for many lower areas. Don't want to make a million plots.
            if len(df_grouped) > 10:
                x = input(upper_area + " has " + str(len(df_grouped)) + " areas to plot.\n"
                                                                        "(1) Skip\n"
                                                                        "(2) Plot\n")
                if x == '1':
                    continue
                else:
                    pass

            for lower_area, df_lower in df_grouped:
                # plot each of the columns as subplots
                for column, [bin_width, [q_low, q_high]] in bins_quantiles.items():
                    print(q_low, q_high)
                    q_low = df_lower[column].quantile(q_low)
                    q_high = df_lower[column].quantile(q_high)
                    df_lower = df_lower.loc[(df_lower[column] < q_high) & (df_lower[column] > q_low)]
                    sns.displot(df_lower[column], x=df_lower[column], binwidth=bin_width)
                    plt.suptitle(upper_area[::-1] + ": " + lower_area[::-1])
                plt.show()

