import database_manager

# TODO: add column for average rank, add column for number of time scanned(for calculating averages)
# TODO descriptions
import fetch_listings
import settings_manager


def main():

    x = input("Select action:\n"
              "(1) Scan the whole country\n"
              "(2) Select areas to scan\n"
              "(3) Scan using urls)\n"
              "(4) Perform a search using a previous search\n"
              "(5) Reset the Database\n"
              "(6) Reset listings History\n"
              "(7) Quit\n")

    while True:
        max_pages = input("Set a limit for number of pages per search:")
        try:
            int(max_pages)
            break
        except ValueError:
            print("Invalid input\n")

    # Scan all areas
    if x == '1':
        url = 'https://www.yad2.co.il/realestate/rent?price=750-10000&squaremeter=0-300'
        print('fetching all rentals:', url)
        fetch_listings.search(url, max_pages)

    # user selects as many areas as they want to scan
    elif x == '2':
        urls = fetch_listings.select_areas_to_scan()
        for url in urls:
            print('fetching:', url)
            fetch_listings.search(url, max_pages)
        pass

    # user inputs as many urls as they want to scan
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
        # save the settings
        settings_manager.save_settings(url_list)

        # start the scan
        for url in url_list:
            fetch_listings.search(url, max_pages)

    # Perform a search using a previously scanned url
    elif x == '4':
        url_list = settings_manager.load_settings()
        for url in url_list:
            fetch_listings.search(url, max_pages)

    # Reset the database
    elif x == "5":
        x = input((print("Are you sure? (y/n)")))
        if x == "y":
            print("\nResetting databse...")
            database_manager.reset_database()
            print("Database Reset.\n")
        main()

    # elif x == "6":
    #     x = input(print("Are you sure?(y/n)"))
    #     if x == "y":
    #         database_manager.reset_database()

    elif x == "9":
        quit()

    else:
        print("Invalid Input")
        main()

    database_manager.close_database()


if __name__ == "__main__":
    main()
