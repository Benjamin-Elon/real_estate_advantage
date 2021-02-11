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
        # iterate over groups so we get an ordered list
        groups = list(listings.groups.__iter__())
        areas_chunked = chunks(groups, 12)
        for area_chunk in areas_chunked:
            fig, axes = plt.subplots(nrows=4, ncols=3, sharex=True)
            for area, ax in zip(area_chunk, axes.flatten(order='F')):
                df_area = listings.get_group(area)
                print(area)
                bin_width = x_axis_med / (math.log(len(df_area), 10) * 5)
                sns.histplot(data=df_area, x=x_axis, ax=ax, kde=kde, binwidth=bin_width)
                ax.title.set_text(area[::-1] + ", n = " + str(len(df_area)))
                # place vertical line on each subplot for median value
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
                    df = df_areas.get_group(area)
                    bin_width = x_axis_med/(math.log(len(df), 10)*5)
                    print(area)
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
        # iterate over groups so we get an ordered list
        groups = list(listings.groups.__iter__())
        # split upper areas into chunks
        areas_chunked = chunks(groups, 12)
        # for chunk
        for area_chunk in areas_chunked:
            fig, axes = plt.subplots(nrows=4, ncols=3, sharex=True, sharey=True)
            # for area in chunk
            for area, ax in zip(area_chunk, axes.flatten(order='F')):
                df_area = listings.get_group(area)
                # print(area)
                # plot area
                sns.scatterplot(x=df_area[x_axis], y=df_area[y_axis], ax=ax)
                ax.title.set_text(area[::-1] + ", n = " + str(len(df_area)))
        plt.tight_layout()
        plt.legend()
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df_areas in listings.items():
            # split lower areas into chunks
            area_chunks = chunks(list(df_areas.groups), 12)
            # for chunk
            for area_chunk in area_chunks:
                n_rows, n_cols = get_fig_dims(len(area_chunk))
                print(n_rows, n_cols)
                # plot each lower area as subplot
                if n_rows == 1 & n_cols == 1:
                    for area, df in df_areas:
                        print(area, df)

                        sns.scatterplot(x=df[x_axis], y=df[y_axis])
                        plt.suptitle(upper_area_name[::-1]+'\n'+area)
                else:
                    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, sharex=True, sharey=True)
                    for area, ax in zip(area_chunk, axes.flatten(order='F')):
                        df = df_areas.get_group(area)
                        # print(area)
                        sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax, hue=df['elevator'])
                        ax.title.set_text(area[::-1] + ", n = " + str(len(df)))

                plt.suptitle(upper_area_name[::-1])
            plt.tight_layout(h_pad=.15, w_pad=.15, rect=[-.05,-.05,.95,.95])
            # plt.subplots_adjust(top=.9)
        plt.show()

    return


def reverse_name_values(df):
    """Reverse hebrew words in a dataframe so that they will be display in the right direction"""

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


def reverse_string_list(str_list):
    """Generator yielding a list of strings with each string reversed"""
    for string in str_list:
        yield string[::-1]


def get_fig_dims(n):
    if n <= 4:
        n_rows = n
        n_cols = 1
    elif n == 5 or n == 6:
        n_rows = 3
        n_cols = 2
    elif n == 7 or n == 8 or n ==9:
        n_rows = 3
        n_cols = 3
    else:
        n_rows = 4
        n_cols = 3

    return n_rows, n_cols


def ridge_plot(listings, x_axis, option, upper_name_column, lower_name_column):
    # filter areas according to sample threshold

    if option == 'up':
        df_1 = pd.DataFrame()
        # combine all lower areas into single df
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        # sort upper areas alphabetically
        df = df_1.sort_values(upper_name_column)
        # group by upper area
        df_grouped = df.groupby(upper_name_column)
        # get list of areas
        area_names = list(df_grouped.groups.__iter__())
        # generate reversed strings for display
        area_names = list(reverse_string_list(area_names))

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
            # get list of areas
            area_names = list(df_grouped.groups.__iter__())
            # generate reversed strings for display
            area_names = list(reverse_string_list(area_names))

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


def display_bar_charts():
    return


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

