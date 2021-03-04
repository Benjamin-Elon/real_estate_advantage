from matplotlib import cm
import joypy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# import sqlite3

# con = sqlite3.connect(r"Database/yad2db.sqlite")
# cur = con.cursor()

# df = pd.read_sql('SELECT * FROM Listings', con)


def display_hists(listings, upper_name_column, lower_name_column, x_axis, scope, kde=False):
    """Displays histograms by locale"""
    # get the median value of the x_axis for all listings
    x_axis_med = listings[x_axis].median()
    # listings = listings[listings[x_axis].notna()]
    listings = listings.groupby(upper_name_column, sort=False)
    # for area, group in listings:
    #     print(area, group[x_axis].describe)

    if scope == 'up':
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
                ax.axvline(x=median, ymin=0, color='r')
                ax.text(median, 2, median, rotation=90)
            plt.tight_layout()
            plt.subplots_adjust(top=.9)
            plt.show()

    elif scope == 'down':
        # for each upper area:
        for upper_area_name, df_up in listings:
            df_down = df_up.groupby(lower_name_column, sort=False)

            area_chunks = chunks(list(df_down.groups), 12)
            # for lower areas chunk
            for area_chunk in area_chunks:
                fig, axes = plt.subplots(nrows=4, ncols=3, sharex=True)
                # plot each lower area as subplot
                for area, ax in zip(area_chunk, axes.flatten(order='F')):
                    df_area = df_down.get_group(area)
                    print(area)
                    print(len(df_area[x_axis]))
                    print(len(df_area[x_axis].notna()))
                    bin_width = x_axis_med/(math.log(len(df_area), 10)*5)
                    sns.histplot(data=df_area, x=x_axis, ax=ax, kde=kde, binwidth=bin_width)
                    ax.title.set_text(area[::-1] + ", n = " + str(len(df_area)))
                    # place vertical line on each subplot for median value
                    median = df_area[x_axis].median()
                    median = round(median, 1)
                    ax.axvline(x=median, ymin=0, color='r')
                    ax.text(median, 2, median, rotation=90)

                # plot all lower areas for each upper area
                plt.suptitle(upper_area_name[::-1])
                plt.tight_layout()
                plt.subplots_adjust(top=.9)
        plt.show()

    return


def display_scatter_plots(listings, upper_name_column, lower_name_column, x_axis, y_axis, option, hue):
    """Displays scatter plots by locale"""
    listings = listings.groupby(upper_name_column)
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
                sns.scatterplot(x=df_area[x_axis], y=df_area[y_axis], ax=ax, hue=df_area[hue], legend='full')

                ax.title.set_text(area[::-1] + ", n = " + str(len(df_area)))

            # add figure legend
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right')

            # remove individual legends
            for ax in axes.flatten():
                ax.legend().remove()

        plt.tight_layout()
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df_up in listings:
            # split lower areas into chunks
            df_down = df_up.groupby(lower_name_column)
            area_chunks = chunks(list(df_down.groups), 12)
            # for chunk
            for area_chunk in area_chunks:
                # TODO: fix auto subplot dimensions, is not working for some reason
                n_rows, n_cols = get_fig_dims(len(area_chunk))
                # if there is a single subplot
                if n_rows == 1 & n_cols == 1:
                    for area, df in df_down:
                        print(area)

                        sns.scatterplot(x=df[x_axis], y=df[y_axis])
                        plt.suptitle(upper_area_name[::-1]+'\n'+area)
                # if there are multiple subplots
                else:
                    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, sharex=True, sharey=True)

                    for area, ax in zip(area_chunk, axes.flatten(order='F')):
                        df = df_down.get_group(area)
                        sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax, hue=df[hue], legend='full')

                        ax.title.set_text(area[::-1] + ", n = " + str(len(df)))
                        ax.set_xlabel(xlabel=x_axis)

                        # add figure legend
                    handles, labels = ax.get_legend_handles_labels()
                    fig.legend(handles, labels, loc='upper right')

                    # remove individual legends
                    for ax in axes.flatten():
                        ax.legend().remove()

                    plt.suptitle(upper_area_name[::-1])
                    plt.tight_layout(h_pad=.15, w_pad=.15, rect=[-.05, -.05, .95, .95])
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
    """Helper for scatter plot.
     Returns: dimensions for subplots [n_rows, n_cols]"""
    if n <= 4:
        n_rows = n
        n_cols = 1
    elif n == 5 or n == 6:
        n_rows = 3
        n_cols = 2
    elif n == 7 or n == 8 or n == 9:
        n_rows = 3
        n_cols = 3
    else:
        n_rows = 4
        n_cols = 3

    return n_rows, n_cols


def ridge_plot(listings, x_axis, scope, upper_name_column, lower_name_column):
    """Displays ridge plots by locale"""

    # get list of reversed areas for display
    listings[upper_name_column] = listings[upper_name_column].apply(lambda x: x[::-1])
    areas = listings[upper_name_column].unique()
    print(areas)
    if scope == 'up':
        # # get list of reversed areas for display
        # areas = listings[upper_name_column].apply(lambda x:x[::-1]).unique()

        # split areas into chunks so the graph isn't cluttered
        areas = chunks(areas, 10)

        # for chunk: graph areas in chunk
        for chunk in areas:
            # print(chunk)
            df_chunk = listings[listings[upper_name_column].isin(chunk)]
            print(df_chunk)
            fig, axes = joypy.joyplot(df_chunk, by=upper_name_column, column=x_axis,
                                      kind="kde",
                                      range_style='own', tails=0.2,
                                      overlap=3, linewidth=1, colormap=cm.autumn_r,
                                      labels=chunk, grid='y', figsize=(8, 2.5 + .5 * len(chunk)),
                                      title=upper_name_column.replace('_', ' ').replace('name', '') + ": " + x_axis)
            plt.show()

    if scope == 'down':

        listings = listings.groupby(upper_name_column)
        # for each upper area
        for upper_area, df_up in listings:

            df_up[lower_name_column] = df_up[lower_name_column].apply(lambda x: x[::-1])

            areas = df_up[lower_name_column].unique()
            area_chunks = chunks(list(areas), 12)

            # for lower areas chunk
            for area_chunk in area_chunks:
                df_down = df_up[df_up[lower_name_column].isin(area_chunk)]
                # joyplot will automatically sort if given a dataframe ungrouped
                df_down = df_down.groupby(lower_name_column, sort=False)

                # print(df_down, len(df_down))
                fig, axes = joypy.joyplot(df_down, by=lower_name_column, column=x_axis,
                                          kind="kde",
                                          range_style='own', tails=0.2,
                                          overlap=3, linewidth=1, colormap=cm.autumn_r,
                                          labels=area_chunk, grid='y', figsize=(8, 2.5 + .5*len(area_chunk)),
                                          title=upper_area.replace('_', ' ').replace('name', '') + ": " + x_axis)

                # TODO: figure out how to get the line and text on top (low priority)
                # for ax, [area, group] in list(zip(axes, df_down)):
                #     median = group[x_axis].median()
                #     median = round(median, 1)
                #     ax.axvline(x=median, ymin=0, ymax=1, color='black')
                #     ax.text(median, -1, 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', rotation=90)

            plt.show()


def multiple_lin_reg_plot(listings, option, x_axis, y_axis, hue, upper_name_column, lower_name_column):

    if option == 'up':
        areas = listings[upper_name_column].apply(lambda x: x[::-1]).unique()
        # areas = list(listings.groups.__iter__())
        areas_chunked = chunks(areas, 12)
        for chunk in areas_chunked:
            df_chunk = listings[listings[upper_name_column].isin(chunk)]
            g = sns.lmplot(data=df_chunk, x=x_axis, y=y_axis, col=upper_name_column, hue=hue, col_wrap=4, lowess=True,
                           height=2, markers='.', palette='muted')
            for ax, area in zip(g.axes.flatten(), areas):
                ax.title.set_text(area + ', n=' + str(len(listings[listings[upper_name_column] == area[::-1]])))
            plt.suptitle(upper_name_column.replace('_', ' ').replace('name', ''))

            plt.tight_layout()
        plt.show()

    if option == 'down':

        df_1 = listings.groupby(upper_name_column)

        # for each upper area
        for upper_area, df_up in df_1:

            # df_down = df_up.groupby(lower_name_column)
            df_up[lower_name_column] = df_up[lower_name_column].apply(lambda x: x[::-1])
            areas = df_up[lower_name_column].unique()

            area_chunks = chunks(list(areas), 12)
            # for lower areas chunk
            for area_chunk in area_chunks:
                df_down = df_up[df_up[lower_name_column].isin(area_chunk)]
                g = sns.lmplot(data=df_down, x=x_axis, y=y_axis, col=lower_name_column, hue=hue, col_wrap=4, lowess=True,height=2, markers='.', palette='muted')
                for ax, area in zip(g.axes.flatten(), areas):
                    ax.title.set_text(area + ', n=' + str(len(df_up[df_up[lower_name_column] == area])))
                plt.suptitle(upper_area[::-1])
                legend = g.legend
                legend.set_bbox_to_anchor([1, .90])
                plt.tight_layout()
                plt.subplots_adjust(top=.9, right=.85)
                plt.show()


def explore_data(listings, scope, upper_name_column, lower_name_column):
    """Quick data exploration using histograms (3x3) subplots with useful parameters"""

    bins_quantiles = {'price': [250, [0.01, .995]], 'price_per_sqmt': [1, [0.01, .99]],
                      'sqmt': [10, [0.05, .985]], 'est_arnona': [50, [.015, .99]], 'rooms': [1, [.0, 1.0]],
                      'floor': [1, [.0, 1.0]], 'building_floors': [1, [.0, 1.0]],
                      'days_on_market': [10, [.01, .98]], 'days_until_available': [10, [.01, .99]]}

    if scope == 'up':
        for area, df in listings:
            fig, axes = plt.subplots(nrows=3, ncols=3)
            print(area)
            for (column, [bin_width, [q_low, q_high]]), ax in zip(bins_quantiles.items(), axes.flatten()):
                # filter out small samples
                df = df.groupby(upper_name_column).filter(lambda r: len(r[r[column].notna()]) > 30)

                sns.histplot(df[column], x=df[column], ax=ax, binwidth=bin_width)

                plt.tight_layout()
                plt.suptitle(area[::-1] + ", n = " + str(len(df)))

        plt.show()

    # TODO: test this
    elif scope == 'down':
        listings = listings.groupby(upper_name_column)
        # for each upper area
        for upper_area, df_up in listings:
            df_low
            # check for many lower areas. Don't want to make a million plots.
            if len(df_low) > 10:
                x = input(upper_area + " has " + str(len(df_low)) + " areas to plot.\n"
                                                                      "(1) Skip\n"
                                                                      "(2) Plot\n")
                if x == '1':
                    continue
                else:
                    pass

            for lower_area, df_low in df_group:
                # plot each of the columns as subplots
                for column, [bin_width, [q_low, q_high]] in bins_quantiles.items():

                    sns.displot(df_low[column], x=df_low[column], binwidth=bin_width)
                    plt.suptitle(upper_area[::-1] + ": " + lower_area[::-1])
                plt.show()

