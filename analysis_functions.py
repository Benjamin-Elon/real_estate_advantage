from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# TODO: add sort by (price, alphabetical, top_x ect)
# TODO: remove area_name


def generate_composite_params(df):
    """takes a dataframe and returns it with a few extra columns"""

    # ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'days_on_market', 'days_until_available']

    df['total_price'] = df['price'] + df['arnona'] + df['vaad_bayit']
    df['arnona_per_sqmt'] = df['arnona'] / df['sqmt']
    df['total_price_per_sqmt'] = df['total_price'] / df['sqmt']
    df['price_per_sqmt'] = df['price'] / df['sqmt']
    last_updated_list = df['updated_at']
    entry_date_list = df['entry_date']
    days_on_market_list = []
    days_until_available_list = []
    for last_update, entry_date in zip(last_updated_list, entry_date_list):
        try:
            time_on_market = \
                (datetime.strptime(last_update, '%Y-%m-%d') - datetime.strptime(entry_date, '%Y-%m-%d')).days
            if time_on_market < 0:
                days_until_available_list.append(np.abs(time_on_market))
            else:
                days_until_available_list.append(np.nan)
            days_on_market_list.append(time_on_market)
        # if row(listing) is missing a date
        except TypeError:
            days_on_market_list.append(np.nan)
            days_until_available_list.append(np.nan)

    df['days_on_market'] = days_on_market_list
    df['days_until_available'] = days_until_available_list

    # fill in neighborhood value based on street and city ids.

    return df


def display_hists(listings, x_axis, option, upper_name_column, lower_name_column):

    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        df_1 = reverse_name_values(df_1)
        df_1 = df_1.sort_values('upper_name_column', ascending=False)
        grid = sns.displot(data=df_1, kind='hist', rug=True, x=x_axis, col=upper_name_column, col_wrap=3)

        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df in listings.items():
            df = reverse_name_values(df)
            # display lower areas as subplots
            df_1 = df_1.sort_values('lower_name_column', ascending=False)
            sns.displot(data=df, kind='hist', rug=True, x=x_axis, col=lower_name_column, col_wrap=3)
            plt.suptitle(upper_area_name[::-1])
            plt.show()

    return


def apply_points(mean):
    ax = plt.vlines(x=mean, ymax=10, ymin=0)


def display_distributions(listings, x_axis, option, upper_name_column, lower_name_column):
    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)
        # insert function for getting a list of means for each grouping
        city = df_1.query('city_name != None')
        city = df_1.groupby(by='city_id')
        means = []
        for city_id, city_df in city:
            mean = int(city_df[x_axis].mean(axis=0))
            means.append(mean)
        df_1 = reverse_name_values(df_1)
        grid = sns.displot(data=df_1, kind='kde', rug=True, x=x_axis, col=upper_name_column, col_wrap=3)
        grid.map(apply_points, (lambda x: x in means), )
        plt.show()

    elif option == 'down':
        # for each upper area:

        for upper_area_name, df in listings.items():

            df = reverse_name_values(df)

            # for area_id in df[lower_name_column]:
            # mean.append(int(df[x_axis].mean(axis=0)))
            # display lower areas as subplots
            sns.displot(data=df, kind='kde', rug=True, x=x_axis, col=lower_name_column, col_wrap=3)
            # grid.map(plt.scatter, x=mean, y=0)
            # grid.map(plt.annotate, text="mean: " + str(mean), xy=(mean, 0))
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

    df_columns = ['top_area_name', 'area_name', 'city_name', 'neighborhood_name', 'street_name', 'contact_name',
                  'listing_id', 'renovated']

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

def apartment_search():
    pass

