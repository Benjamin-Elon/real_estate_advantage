from datetime import datetime
import numpy as np
import pandas as pd
import sqlite3

con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

# impute arnona from average cost per neighborhood
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter


int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
                     'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available']

date_range_columns = ['date_added', 'updated_at']

bool_columns = ['ac', 'b_shelter',
                'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
                'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
                'long_term', 'pandora_doors', 'furniture_description', 'description']
option_columns = ['apt_type', 'apartment_state']

quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

# if you only want to see listings with extra info
scan_state_column = ['extra_info']

# (having a list of areas doesn't tell you where they are relative to each other, other than 'x in y')
geo_coord_columns = ['latitude', 'longitude']


# TODO: extract arnona fom descriptions. low priority
def get_arnona_from_desc():
    return


# TODO: finish this
# infer price from price per sqmt
def infer_missing_values(df):
    """
    takes dataframe of listings. infers arnona, and price values
    update Listings table with new columns
    """

    # get all neighborhood with more than 30 listings
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods WHERE n > 30', con)
    df_listings = pd.read_sql('SELECT * FROM Listings', con)

    df_neighborhoods = df_neighborhoods[['neighborhood_id', 'arnona_per_sqmt']]

    # merge average neighborhood values into Listings table
    df = df.merge(right=df_neighborhoods, how='left', right_on='neighborhood_id', left_on='neighborhood_id')
    pd.DataFrame.rename(df, columns={'arnona_per_sqmt_y': 'arnona_per_sqmt'}, inplace=True)

    # create some more composite values in Listings Table
    df['est_arnona'] = df['sqmt'] * df['arnona_per_sqmt']
    df['arnona_ratio'] = (df['arnona'] / df['est_arnona'])

    # df = df[(df['arnona_ratio'] > .65) & (df['arnona_ratio'] < 1.35)]
    # # update listing table with new values
    # for index, row in df.iterrows():
    #
    #     con.execute('UPDATE Listings SET (est_arnona, arnona_ratio) = (?,?) WHERE listing_id = (?)',
    #                 (row['est_arnona'], row['arnona_ratio'], row['listing_id']))

    # con.commit()
    # cur.close()
    return df


def update_composite_params(df):
    """takes Listing dataframe, adds columns:
    [total_price, arnona_per_sqmt, price_per_sqmt, days_on_market, days_until_available]
    """

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

    return df


def update_locales_avgs():
    """generates columns [smqt, arnona_per_sqmt, latitude, longitude, n(sample_size)] for each locale.
    Updates the area database tables with new columns
    """

    print('Updating locale values...')

    df = pd.read_sql('SELECT * FROM Listings', con)
    locales = [['top_area_id', 'Top_areas'], ['area_id', 'Areas'], ['city_id', 'Cities'],
               ['neighborhood_id', 'Neighborhoods'], ['street_id', 'Streets']]

    for column_name, table_name in locales:
        print(table_name)

        df_1 = df.groupby([column_name]).agg({'sqmt': ['median'], 'arnona': ['median'],
                                              'latitude': ['mean'], 'longitude': ['mean'], 'price': ['median']})

        df_1.columns = df_1.columns.map('_'.join)
        df_1 = df_1.reset_index()
        n = df[column_name].value_counts().reset_index(name='n')

        df_1 = df_1.merge(right=n, how='left', right_on='index', left_on=column_name)

        for index, row in df_1.iterrows():
            n = row['n']
            # 30 is minimum sample size
            if n < 30:
                arnona = None
                sqmt = None
                price = None
                arnona_per_sqmt = None
                price_per_sqmt = None

            else:
                arnona = row['arnona_median']
                sqmt = row['sqmt_median']
                price = row['price_median']

                arnona_per_sqmt = arnona / sqmt
                arnona_per_sqmt = round(arnona_per_sqmt, 2)

                price_per_sqmt = price / sqmt
                price_per_sqmt = round(price_per_sqmt, 2)

            latitude = row['latitude_mean']
            longitude = row['longitude_mean']

            area_id = str(row[column_name])

            query = 'UPDATE ' + table_name + \
                    ' SET (arnona_per_sqmt, sqmt, price, arnona, price_per_sqmt, latitude, longitude, n) = (?,?,?,?,?,?,?,?) ' \
                    'WHERE ' + column_name + ' = (?)'
            con.execute(query, (arnona_per_sqmt, sqmt, price, arnona, price_per_sqmt, latitude, longitude, n, area_id))

        con.commit()
    cur.close()
    print("Done.")

    return


def apply_constraints(df, constraints):
    print("Applying constraints...")

    # toss outliers for each variable
    try:
        if constraints['toss_outliers'] is not None:
            df = toss_outliers(df, constraints)
    except TypeError:
        pass

    # apply range constraints
    try:
        if constraints['range'] is not None:
            for column in int_range_columns:
                if constraints['range'][column] is not None:
                    low, high = constraints['range'][column]

                    df = df[(df[column] < high) & (df[column] > low)]
    except TypeError:
        pass

    # bool constraints
    try:
        if constraints['bool'] is not None:
            for column in bool_columns:
                if constraints['bool'][column] is not None:
                    # value can be 0 or 1
                    value = constraints['bool'][column]
                    df = df.loc[df['roommates'] == value]
    except TypeError:
        pass

    return df


def toss_outliers(df, constraints):
    for column in quantile_columns:

        if constraints['toss_outliers'][column] is not None:
            q_low, q_high = constraints['toss_outliers'][column]
            # convert to percentiles
            q_low = float(q_low * .01)
            q_high = float(q_high * .01)
            q_low = df[column].quantile(q_low)
            q_high = df[column].quantile(q_high)

            # sometimes neighborhood can be none, but city always has a value.
            # group df locale, toss outliers, and append each group back together into a single df
            neighborhood = df.query('neighborhood_name != None')
            neighborhood = neighborhood.groupby(by='neighborhood_id')

            city = df.query('city_name != None & neighborhood_name == None')
            city = city.groupby(by='city_id')

            df_1 = pd.DataFrame()
            for neighborhood_id, neighborhood_df in neighborhood:
                # print(len(neighborhood_df))
                neighborhood_df = neighborhood_df.loc[
                    (neighborhood_df[column] < q_high) & (neighborhood_df[column] > q_low)]
                # print(len(neighborhood_df))
                df_1 = df_1.append(neighborhood_df)

            for city_id, city_df in city:
                # orig_len = len(city_df)
                city_df = city_df.loc[
                    (city_df[column] < q_high) & (city_df[column] > q_low)]
                # print(len(city_df))
                df_1 = df_1.append(city_df)

            df = df_1

    print("done.\n")

    return df


def get_listings(df, area_settings):
    """Fetches the listings from database using the area settings"""
    """Returns: {{upper_area: df_of_lower_areas},..."""
    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']],
    # [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130,
    # 'אזור']]]]

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

    listings = {}

    upper_scope_name, lower_scope_name = area_settings[0]
    upper_id_column, upper_name_column = scope_names[upper_scope_name]
    lower_id_column, lower_name_column = scope_names[lower_scope_name]

    area_settings = area_settings[1:]

    for upper_area, lower_areas in zip(area_settings[0], area_settings[1]):
        area_ids = []
        upper_name = upper_area[1]
        upper_id = upper_area[0]
        for lower_id, lower_name in lower_areas:
            area_ids.append(lower_id)
        listings[upper_name] = df.loc[df[lower_id_column].isin(area_ids) & (df[upper_id_column] == upper_id)]

    return listings, upper_name_column, lower_name_column


def infer_neighborhood(df):
    # fill in neighborhood value based on street and city ids.
    return df