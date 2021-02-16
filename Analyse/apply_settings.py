from datetime import datetime
import numpy as np
import pandas as pd
import sqlite3

con = sqlite3.connect(r"Database/yad2db.sqlite")
cur = con.cursor()

# impute arnona from average cost per neighborhood
# derive vaad bayit from other listings in same building
# Find actual price for roommate listings / filter


# int_range_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'balconies',
#                      'rooms', 'floor', 'building_floors', 'days_on_market', 'days_until_available']

# date_range_columns = ['date_added', 'updated_at']

# bool_columns = ['ac', 'b_shelter',
#                 'furniture', 'central_ac', 'sunroom', 'storage', 'accesible', 'parking',
#                 'pets', 'window_bars', 'elevator', 'sub_apartment', 'renovated',
#                 'long_term', 'pandora_doors', 'furniture_description', 'description']
# option_columns = ['apt_type', 'apartment_state']

# quantile_columns = ['price', 'vaad_bayit', 'arnona', 'sqmt', 'arnona_per_sqmt']

# if you only want to see listings with extra info
# scan_state_column = ['extra_info']

# (having a list of areas doesn't tell you where they are relative to each other, other than 'x in y')
# geo_coord_columns = ['latitude', 'longitude']


# TODO: extract arnona fom descriptions. low priority
def get_arnona_from_desc():
    return


def clean_listings(df):
    """
    Removes listings from df based on the composite parameters
    ['arnona_per_sqmt', 'total_price_per_sqmt', 'price_per_sqmt']
    Returns: df
    """
    print('cleaning listings...')
    # get all neighborhood with more than 30 listings
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods WHERE n > 30', con)

    df_neighborhoods = df_neighborhoods[['neighborhood_id', 'arnona_per_sqmt', 'price_per_sqmt']]

    # merge average neighborhood values into Listings table
    df = df.merge(right=df_neighborhoods, how='left', right_on='neighborhood_id', left_on='neighborhood_id')
    pd.DataFrame.rename(df, columns={'arnona_per_sqmt_y': 'avg_arnona_per_sqmt',
                                     'arnona_per_sqmt_x': 'arnona_per_sqmt',
                                     'price_per_sqmt_y': 'avg_price_per_sqmt',
                                     'price_per_sqmt_x': 'price_per_sqmt'}, inplace=True)

    # create some more composite values in Listings Table
    # est_arnona is the predicted arnona rate
    df['est_arnona'] = df['sqmt'] * df['avg_arnona_per_sqmt']
    df = df[df['avg_arnona_per_sqmt'].notna()]
    # arnona_ratio is the variance from the predicted arnona
    df['arnona_ratio'] = (df['arnona'] / df['est_arnona'])
    # est_price is the predicted price
    df['est_price'] = df['sqmt'] * df['avg_price_per_sqmt']
    # price_ratio is the variance from the predicted price
    df['price_ratio'] = df['price'] / df['est_price']
    # print(df['price_ratio'].quantile(.97))

    # remove listings with unrealistic ratios
    df = df[((df['arnona_ratio'] > .5) & (df['arnona_ratio'] < 1.55)) | df['arnona_ratio'].isna()]
    df = df[((df['price_ratio'] > .6) & (df['price_ratio'] < 2)) | df['price_ratio'].isna()]

    return df


def to_days(x):
    """Converts datetime to days"""
    return x.days


def update_composite_params(df):
    """
    Takes Listing df, adds columns:
    [total_price, arnona_per_sqmt, price_per_sqmt, days_on_market, days_until_available]
    Updates Listings table
    Returns: df
    """
    print('Updating composite params...')
    # ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'days_on_market', 'days_until_available']

    df['total_price'] = df['price'] + df['arnona'] + df['vaad_bayit']
    df['arnona_per_sqmt'] = df['arnona'] / df['sqmt']
    df['total_price_per_sqmt'] = df['total_price'] / df['sqmt']
    df['price_per_sqmt'] = df['price'] / df['sqmt']

    # convert columns to datetime
    df['days_since_update'] = (datetime.today() - pd.to_datetime(df['updated_at'], format='%Y-%m-%d'))
    df['days_since_update'] = df['days_since_update'].apply(to_days)
    df['age'] = (pd.to_datetime(df['updated_at'], format='%Y-%m-%d') - pd.to_datetime(df['entry_date'],
                                                                                      format='%Y-%m-%d'))
    df['age'] = df['age'].apply(to_days)
    # print(df['age'])
    df['days_until_available'] = df.loc[df['age'] <= 0, 'age']
    df['days_until_available'] = df['days_until_available'].abs()
    df['days_on_market'] = df.loc[df['age'] >= 0, 'age']

    for index, row in df.iterrows():
        con.execute('UPDATE Listings SET (total_price, arnona_per_sqmt, total_price_per_sqmt, price_per_sqmt, '
                    'days_on_market, days_until_available, days_since_update) = (?,?,?,?,?,?,?) '
                    'WHERE listing_id = (?)',
                    (row['total_price'], row['arnona_per_sqmt'], row['total_price_per_sqmt'], row['price_per_sqmt'],
                     row['days_on_market'], row['days_until_available'], row['days_since_update'], row['listing_id']))
    con.commit()
    return df


def update_locales_avgs():
    """
    Generates columns [smqt, arnona_per_sqmt, latitude, longitude, n(sample_size)] for each locale.
    Updates the area database tables with new columns
    Returns: None
    """
    print('Updating area averages...')

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
    """
    Applies constraints on a df of listings
    Returns: df
    """
    print("Applying constraints...\n")

    # toss outliers for each variable
    if constraints['toss_outliers'] is not None:
        df = toss_outliers(df, constraints)

    # apply range constraints
    if constraints['range'] is not None:
        for column, [low, high] in constraints['range'].items():
            print(column)
            print(low, high)
            print('before', len(df))
            df_na = df[df[column].isna()]
            df = df[(df[column] <= high) & (df[column] >= low)]
            df = df.append(df_na)
            print('after', len(df))


    # bool constraints
    if constraints['bool'] is not None:
        for column, value in constraints['bool'].items():
            print(column)
            print('before', len(df))
            value = constraints['bool'][column]
            df_na = df[df[column].isna()]
            df = df.loc[df[column] == value]
            df = df.append(df_na)
            print('after', len(df))

    print(len(df))
    print(df.shape)
    print("SAVING TEST DATABASE")
    con_1 = sqlite3.connect('Database/yad2_verify_settings.sqlite')
    cur_1 = con_1.cursor()
    cur_1.executescript("DROP TABLE IF EXISTS Listings;")
    df.to_sql('Listings', con_1, if_exists='replace')
    con_1.commit()
    con_1.close()

    return df


def apply_quantiles(q_low, q_high, df, column):
    """
    Toss listings according quantiles based on locale averages (neighborhood or city)
    Returns: df
    """
    print("Applying quantiles...")
    # sometimes neighborhood can be none, but city always has a value.
    # group df locale, toss outliers, and append each group back together into a single df
    # get all listings by neighborhood
    neighborhoods = df[df["neighborhood_name"].notna()]
    neighborhood_grouped = neighborhoods.groupby(by='neighborhood_id')
    # get all listings with city and no neighborhood
    cities = df[(df['city_name'].notna()) & (df['neighborhood_name'].isna())]
    city_grouped = cities.groupby(by='city_id')

    df_1 = pd.DataFrame()
    for neighborhood_id, neighborhood_df in neighborhood_grouped:
        v_low = neighborhood_df[column].quantile(q_low)
        v_high = neighborhood_df[column].quantile(q_high)
        df_na = neighborhood_df[neighborhood_df[column].isna()]
        neighborhood_df = neighborhood_df.loc[(neighborhood_df[column] < v_high) & (neighborhood_df[column] > v_low)]

        df_1 = df_1.append(neighborhood_df)
        df_1 = df_1.append(df_na)

    for city_id, city_df in city_grouped:
        v_low = city_df[column].quantile(q_low)
        v_high = city_df[column].quantile(q_high)
        df_na = city_df[city_df[column].isna()]
        city_df = city_df.loc[(city_df[column] < v_high) & (city_df[column] > v_low)]
        df_1 = df_1.append(city_df)
        df_1 = df_1.append(df_na)

    df = df_1

    return df


def toss_outliers(df, constraints):
    """Tosses outliers from the dataframe of listings"""
    if constraints['toss_outliers'] is not None:
        # print("Tossing outliers...")
        for column, [q_low, q_high] in constraints['toss_outliers'].items():
            print(column)
            print("before", len(df))
            df = apply_quantiles(q_low, q_high, df, column)
            print("after", len(df))

        print("done.\n")

    return df


def get_listings(df, area_settings):
    """
    Fetches the listings from database using the area settings
    Returns: {{upper_area: df_of_lower_areas},...
    """

    print("Fetching table rows...")
    # area_selection = [['Areas', 'Cities'], [[18, 'חיפה והסביבה'], [22, 'תל אביב יפו'], [27, 'חולון - בת ים']],
    # [[[18, 'חיפה'], [83, 'טירת כרמל'], [264, 'נשר']], [[22, 'תל אביב יפו']], [[27, 'חולון'], [126, 'בת ים'], [130,
    # 'אזור']]]]

    scope_names = {'Top_areas': ['top_area_id', 'top_area_name'], 'Areas': ['area_id', 'area_name'],
                   'Cities': ['city_id', 'city_name'], 'Neighborhoods': ['neighborhood_id', 'neighborhood_name'],
                   'Streets': ['street_id', 'street_name']}

    listings = {}

    # get upper and lower scope names from current settings
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


def sort_areas(df, sort_type, scope_name_column, x_axis=None, y_axis=None):
    """Sorts a dataframe according to selected sort
    Returns: df"""

    if sort_type == 'alphabetical':
        df = df.sort_values(by=scope_name_column, ascending=False)

    elif sort_type == 'numerical':
        df['area_median'] = df.groupby([scope_name_column])[x_axis].transform('median')
        df = df.sort_values(by='area_median')

    return df
