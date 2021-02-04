import random

import Analyse.analysis_main as analysis_main
import Database.database as database

import Scrape.scrape_listings as scrape_listings
import Settings.settings_manager as settings_manager


def set_max_pages():
    while True:
        max_pages = input("Set a limit for number of pages per search:")
        try:
            int(max_pages)
            break
        except ValueError:
            print("Invalid input\n")

    return max_pages


def main():

    x = input("Select action:\n"
              "(1) Scan a specific url\n"
              "(2) Select areas to scan\n"
              "(3) Set a search profile\n"
              "(4) Perform a search using a previous search\n"
              "(5) Analyse Data\n"
              "(6) Reset settings\n"
              "(7) Reset the Database\n"
              "(9) Quit\n")

    # Scan all areas
    if x == '1':
        url = input("paste url here:\n")
        # url = 'https://www.yad2.co.il/realestate/rent?price=750-10000&squaremeter=0-300'
        print('Scanning url:', url)
        max_pages = set_max_pages()
        scrape_listings.search(url, max_pages)

    # user selects as many areas as they want to scan
    elif x == '2':
        urls = scrape_listings.select_areas_to_scan()
        max_pages = set_max_pages()

        for url in urls:
            print('fetching:', url)
            scrape_listings.search(url, max_pages)
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
            settings_manager.save_settings(url_list, 'search_urls')

        random.shuffle(url_list)
        max_pages = set_max_pages()

        # start the scan
        for url in url_list:
            scrape_listings.search(url, max_pages)

    # load a search profile
    elif x == '4':
        url_list = settings_manager.load_settings('search_urls')

        max_pages = set_max_pages()

        for url in url_list:
            scrape_listings.search(url, max_pages)

    # analyse data
    elif x == "5":
        analysis_main.top_menu()

    # reset settings
    elif x == '6':
        settings_manager.delete_settings()
        print("Settings deleted.\n")

    # Reset the database
    elif x == "7":
        x = input((print("This will delete all the scraped listings.\n"
                         "Are you sure? (y/n)\n")))
        if x == "y":
            print("\nResetting database...")
            database.delete_listing_table()
            print("Database Reset.\n")
        main()

    elif x == "9":
        quit()

    else:
        print("Invalid Input")

    main()

    database.close_database()


if __name__ == "__main__":
    main()
