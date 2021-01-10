import database_manager


# TODO: add column for average rank, add column for number of time scanned(for calculating averages)
import fetch_listings


def main():

    scan_list = ['https://www.yad2.co.il/realestate/rent?topArea=25&price=750-2000&squaremeter=30-80',
                 'https://www.yad2.co.il/realestate/rent?area=74']

    x = input("Select action:\n"
              "(0) Perform a new search\n"
              "(1) Perform full scan: Scan a list of urls\n"

              "(4) Reset the Database\n"
              "(5) Reset listings History\n"
              "(9) Quit\n")
    # "(2) View list of Scan Profiles\n"
    # "(3) Perform a search using a previously scanned url\n"

    # Perform a new search
    if x == '0':
        firt_page_url = input("Paste search search_url from Yad2:")
        first_page_url = 'https://www.yad2.co.il/realestate/rent?price=1000-1500&squaremeter=50-100'
        print(first_page_url)
        fetch_listings.search(first_page_url)

    # Perform full scan: Scan a list of urls
    elif x == "1":
        for url in scan_list:
            fetch_listings.search(url)

    # # View list of Scanner urls
    # elif x == "2":
    #     for url in scan_list:
    #         print (url)
    #     pass
    #
    # # Perform a search using a previously scanned url
    # elif x == '3':
    #     url = fetch_from_d.get_url_list()
    #     if url is None:
    #         scan_url.scan_url(url)

    # Reset the database
    elif x == "4":
        x = input((print("Are you sure? (y/n)")))
        if x == "y":
            print("\nResetting databse...")
            database_manager.reset_database()
            print("Database Reset.\n")
        main()

    elif x == "5":
        x = input(print("Are you sure?(y/n)"))
        if x == "y":
            database_manager.reset_database()

    elif x == "9":
        quit()

    else:
        print("Invalid Input")
        main()

    database_manager.close_database()


    # # Reset the db
    # if x == "1":
    #     build_db.reset_database()
    #     reset_history = input("Do you want to wipe listing history as well? (y/n)\n")
    #     if reset_history == "y":
    #         build_db.reset_history()


if __name__ == "__main__":
    main()
