from matplotlib import cm
import joypy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


# TODO: add sort by (price, alphabetical, top_x ect)
# TODO: remove variable name...grr


def display_hists(listings, x_axis, option, upper_name_column, lower_name_column):
    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        df_1 = reverse_name_values(df_1)
        df_1 = df_1.sort_values(upper_name_column, ascending=False)
        sns.displot(data=df_1, kind='hist', rug=True, x=x_axis, col=upper_name_column, col_wrap=3)

        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df in listings.items():
            df = reverse_name_values(df)
            # display lower areas as subplots
            df = df.sort_values(lower_name_column, ascending=False)
            sns.displot(data=df, kind='hist', rug=True, x=x_axis, col=lower_name_column, col_wrap=3)
            plt.suptitle(upper_area_name[::-1])
        plt.show()

    return


# def apply_points(mean):
#     ax = plt.vlines(x=mean, ymax=10, ymin=0)


def display_kde_dists(listings, x_axis, option, upper_name_column, lower_name_column):
    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)
        # insert function for getting a list of means for each grouping
        city = df_1.query('city_name != None')
        city = df_1.groupby(by='city_id')
        means = []
        # TODO: finish this or don't
        for city_id, city_df in city:
            mean = int(city_df[x_axis].mean(axis=0))
            means.append(mean)
        df_1 = reverse_name_values(df_1)
        sns.displot(data=df_1, kind='kde', rug=True, x=x_axis, col=upper_name_column, col_wrap=3)
        plt.show()

    elif option == 'down':
        # for each upper area:

        for upper_area_name, df in listings.items():
            df = reverse_name_values(df)

            # display lower areas as subplots
            sns.displot(data=df, kind='kde', rug=True, x=x_axis, col=lower_name_column, col_wrap=3)

            plt.suptitle(upper_area_name[::-1])
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
