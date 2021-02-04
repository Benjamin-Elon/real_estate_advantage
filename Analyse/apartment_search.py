import sqlite3
import Settings.settings_manager as settings_manager

con = sqlite3.connect(r"yad2db.sqlite")
cur = con.cursor()

columns = ['apt_type', 'apartment_state', 'total_price', 'arnona_per_sqmt',
           'total_price_per_sqmt', 'price_per_sqmt', 'days_on_market',
           'days_until_available']

default_cols = ['street_name', 'price', 'listing_id']


def top_menu(constraints, listings, upper_name_column, lower_name_column):
    while True:
        x = input("Select action:\n"
                  "(1) Create a new apartment search profile\n"
                  "(2) Load and existing profile\n")
        if x == '1':
            search_profile = create_apt_search_profile()
            settings_manager.save_settings(search_profile, 'search_profile')
        elif x == '2':
            search_profile = settings_manager.load_settings('search_profile')
        else:
            print("Invalid selection...")
            continue
        break

    # fetch results based on the search profile
    print("fetching results...")
    fetch_results(constraints, search_profile, listings, upper_name_column, lower_name_column)


def create_apt_search_profile():
    """Users sets which results they want to display
    returns a search profile: {{column_name: [ascending, option_name, number_of_results],...}}"""

    search_profile = {}
    count = 1

    column_dict = {
        ('Cheapest', 'Most expensive'): ['total_price', 'arnona_per_sqmt', 'total_price_per_sqmt', 'price_per_sqmt'],
        ('Fewest', 'Most'): ['days_on_market', 'days_until_available', 'days_on_market']}

    for options, column_names in column_dict.items():

        # for each column, select high to low or low to high
        for column_name in column_names:
            print("(" + str(count) + "/7)")
            low_option, high_option = options

            count += 1
            while True:
                x = input("Set sort:\n"
                          "(1) " + low_option + " [" + column_name + "]\n"
                          "(2) " + high_option + " [" + column_name + "]\n"
                          "(3) Pass\n")

                if x == '1':
                    search_profile[column_name] = ['True', low_option]
                    break
                elif x == '2':
                    search_profile[column_name] = ['False', high_option]
                    break
                elif x == '3':
                    search_profile[column_name] = None
                    break
                else:
                    print("Invalid selection...")
            if x != '3':
                while True:
                    num = input("Set number of results for[" + column_name + "]:\n")
                    try:
                        num = int(num)
                        search_profile[column_name].append(num)
                        break
                    except ValueError:
                        print("Invalid selection...")

    return search_profile


# TODO: figure out what I was thinking here
def fetch_results(constraints, search_profile, listings, upper_name_column, lower_name_column):
    """search_profile = {{column_name: [ascending, option_name, number_of_results],...}}
       listings = {{upper_area: df_of_lower_areas},...
       constraints = {{'toss_outliers': {column: quantile_range},...
                      {'bool': {column: value},...
                      {'range': {column: value_range},...}"""

    columns_to_display = []
    # display the columns included in constraints
    for constraint in constraints.values():
        if constraint is not None:
            for column_name, value in constraint.items():
                if value is not None:
                    columns_to_display.append(column_name)

    # df = pd.read_sql('SELECT * FROM Listings', con)
    # df = analysis_functions.generate_composite_params(df)

    # for each selected metric
    for column_name, values in search_profile.items():
        ascending, option_name, number_of_results = values

        # for upper each area
        for upper_area, df in listings.items():

            print(upper_name_column + ": " + upper_area + "\n")
            # group each area according to lower areas and sort groups according to metric
            df_grouped = df.sort_values([option_name], ascending=ascending).groupby(lower_name_column)
            # trim columns
            df_grouped = df_grouped[columns_to_display]

            # display results for each lower area
            for area_id, area_df in df_grouped:
                print(area_df.head(number_of_results))
