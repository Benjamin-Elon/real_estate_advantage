import pandas as pd
import sqlite3

con = sqlite3.connect(r"yad2db.sqlite")
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

# if you only want to see listings with extra info
scan_state_column = ['extra_info']

# (having a list of areas doesn't tell you where they are relative to each other, other than 'x in y')
geo_coord_columns = ['latitude', 'longitude']


# TODO: extract arnona fom descriptions. low priority
def get_arnona_from_desc():
    return


# TODO: get average arnona per sqmt per locale
def impute_arnona():
    return


def update_geo_coords():
    """generate average geographic coordinates for each locale, updates the sql database"""

    df = pd.read_sql('SELECT * FROM Listings', con)

    df_top_areas = pd.read_sql('SELECT * FROM Top_areas', con)
    df_areas = pd.read_sql('SELECT * FROM Areas', con)
    df_cities = pd.read_sql('SELECT * FROM Cities', con)
    df_neighborhoods = pd.read_sql('SELECT * FROM Neighborhoods', con)
    df_streets = pd.read_sql('SELECT * FROM Streets', con)


    scope_names = ['Top_areas', 'Areas', 'Cities', 'Neighborhoods', 'Streets']
    id_column_names = ['top_area_id', 'area_id', 'city_id', 'neighborhood_id', 'street_id']
    df_list = [df_top_areas, df_areas, df_cities, df_neighborhoods, df_streets]

    for df_name, id_column, locale_df in list(zip(scope_names, id_column_names, df_list)):
        print("Updating: " + df_name + "...")
        # df = df.sort_values(id_column)
        # locale_df.sort_values(id_column)

        area_groups = df.groupby(id_column)
        for area_id, area_df in area_groups:
            locale_df.loc[locale_df[id_column] == area_id, 'latitude'] = area_df['latitude'].mean()
            locale_df.loc[locale_df[id_column] == area_id, 'longitude'] = area_df['longitude'].mean()
        locale_df.to_sql(df_name, con=con, if_exists='replace', index=None)

    print("done.")
    con.close()

    return


def apply_constraints(df, constraints):
    print("Applying constraints...")
    # toss outliers for each variable
    if constraints['toss_outliers'] is not None:
        df = toss_outliers(df, constraints)

    # apply range constraints
    if constraints['range'] is not None:
        for column in int_range_columns:
            if constraints['range'][column] is not None:
                low, high = constraints['range'][column]

                df = df[(df[column] < high) & (df[column] > low)]

    # bool constraints
    if constraints['bool'] is not None:
        for column in bool_columns:
            if constraints['bool'][column] is not None:
                # value can be 0 or 1
                value = constraints['bool'][column]
                df = df.loc[df['roommates'] == value]

    return df


def toss_outliers(df, constraints):
    for column in int_range_columns:

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
