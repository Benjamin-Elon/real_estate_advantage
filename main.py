import analysis_main
import database

# TODO: add column for average rank, add column for number of time scanned(for calculating averages)
# TODO descriptions
import fetch_listings
import settings_manager


def main():

    x = input("Select action:\n"
              "(1) Scan a specific url\n"
              "(2) Select areas to scan\n"
              "(3) Set a search profile\n"
              "(4) Perform a search using a previous search\n"
              "(5) Reset the Database\n"
              "(6) Analyse Data\n"
              # "(7) Reset listings History\n"
              "(9) Quit\n")

    # Scan all areas
    if x == '1':
        url = input("paste url here:\n")
        # url = 'https://www.yad2.co.il/realestate/rent?price=750-10000&squaremeter=0-300'
        print('Scanning url:', url)
        fetch_listings.search(url)

    # user selects as many areas as they want to scan
    elif x == '2':
        urls = fetch_listings.select_areas_to_scan()
        for url in urls:
            print('fetching:', url)
            fetch_listings.search(url)
        pass

    # user inputs as many area urls as they want to scan. Keep the url params consistent if using the data for visuals.
    elif x == "3":
        url_list = []
        while True:
            url = input("url:\n")
            if url == '' and url_list == []:
                print("No input\n")
                break
            elif url == '':
                break
            else:
                url_list.append(url)
        x = input("Save? (y/n)\n")
        if x == 'y':
            settings_manager.save_settings(url_list)

        # start the scan
        for url in url_list:
            fetch_listings.search(url)

    # load a search profile
    elif x == '4':
        url_list = settings_manager.load_settings()
        for url in url_list:
            fetch_listings.search(url)

    # Reset the database
    elif x == "5":
        x = input((print("Are you sure? (y/n)\n")))
        if x == "y":
            print("\nResetting database...")
            database.reset_database()
            print("Database Reset.\n")
        main()

    # elif x == "7":
    #     x = input(print("Are you sure?(y/n)"))
    #     if x == "y":
    #         database_manager.reset_database()

    elif x == "6":
        analysis_main.top_menu()

    elif x == "9":
        quit()

    else:
        print("Invalid Input")
        main()

    database.close_database()


if __name__ == "__main__":
    main()
