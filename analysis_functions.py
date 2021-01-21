from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def generate_composite_params(df):
    """takes a dataframe and returns it with  a few extra columns"""

    # ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'days_on_market', 'days_until_available']

    df['total_price'] = df['price'] + df['arnona'] + df['vaad_bayit']
    df['arnona_per_sqmt'] = df['arnona'] / df['sqmt']
    df['total_price_per_sqmt'] = df['total_price'] / df['sqmt']
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

    return df


def display_hists(listings, y_axis):
    # for each upper area:
    for upper_area_name, listings in listings.items():

        # display each lower area as a bin
        fig, ax = plt.subplots(len(listings), 1, figsize=(10, 10))
        # Plots do not play nice with hebrew text. Reverse the strings.
        upper_area_name = upper_area_name[::-1]
        fig.suptitle(upper_area_name, fontsize=16)

        x = 0
        for area_name, df in listings.items():
            y_axis = df[y_axis]
            sns.displot(y_axis, ax=ax[x], kind="kde", rug=True)
            area_name = area_name[::-1]
            ax[x].set_title(area_name)
            x += 1

        plt.show()

    return


# TODO: generate standard y-axis scale for better comparison
def display_distributions(listings, x_axis, option, upper_name_column, lower_name_column):
    if option == 'up':
        df_1 = pd.DataFrame()
        for upper_area_name, df in listings.items():
            df_1 = df_1.append(df)

        sns.displot(data=df_1, kind='kde', rug=True, x=x_axis, col=upper_name_column, col_wrap=3)
        plt.show()

    elif option == 'down':
        # for each upper area:
        for upper_area_name, df in listings.items():
            # display lower areas as subplots
            sns.displot(data=df, kind='kde', rug=True, x=x_axis, col=lower_name_column, col_wrap=3)
            plt.suptitle(upper_area_name)
            plt.show()

    return


def display_scatter_plots(listings, x_axis, y_axis, option):

    # make single plot
    if option == 'up':
        n = len(listings)
        fig, ax = plt.subplots(n, 1, figsize=(10, n * 5 + 5))

        # for each upper area:
        x = 0
        for upper_area_name, low_scopes in listings.values():
            # lump all lower areas per upper area
            df = pd.DataFrame()
            for df_1 in low_scopes.values():
                df.append(df_1)

        x_axis = df[x_axis]
        y_axis = df[y_axis]
        sns.scatterplot(x=x_axis, y=y_axis, data=listings)
        ax.set(xlabel=x_axis, ylabel=y_axis)
        ax[x].set_title(upper_area_name)
        x += 1

        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.show()

    elif option == 'down':

        # for each upper area:
        for upper_area_name, listings in listings.items():

            # display lower areas as subplots:
            n = len(listings)
            fig, ax = plt.subplots(n, 1, figsize=(10, n * 5 + 5))

            upper_area_name = upper_area_name[::-1]
            fig.suptitle(upper_area_name, fontsize=16)

            x = 0

            for area_name, df in listings.items():
                x_axis = df[x_axis]

                # price = df['price']
                # average_price = price.mean()
                # print("average price for ", area_name, ":", average_price)

                sns.scatterplot(x=x_axis, y=y_axis, ax=ax[x])

                area_name = area_name[::-1]
                ax[x].set_title(area_name, )
                x += 1
                plt.xlabel(x_axis)
                plt.ylabel(y_axis)
            plt.show()

    return


def apartment_search():
    pass


