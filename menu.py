

# TODO: add column for average rank, add column for number of time scanned(for calculating averages)
def main():

    scan_list = ['https://www.yad2.co.il/realestate/rent?topArea=25&price=750-2000&squaremeter=30-80',
                 'https://www.yad2.co.il/realestate/rent?area=74']

    x = input("Select action:\n"
              "(0) Perform a new search\n"
              "(1) Perform full scan: Scan a list of urls\n"
              "(2) View list of Scanner urls\n"
              "(3) Perform a search using a previously scanned url\n"
              "(4) Reset the Database\n"
              "(5) Reset listings History\n"
              "(9) Quit\n")

    # Perform a new search
    if x == '0':
        url = input("Paste search search_url from Yad2:")
        url = 'https://www.yad2.co.il/realestate/rent?topArea=25&price=750-5000&squaremeter=35-180'
        print(url)
        scan_url.scan_url(url)

    # Perform full scan: Scan a list of urls
    elif x == "1":
        for url in scan_list:
            scan_url.scan_url(url)

    # View list of Scanner urls
    elif x == "2":
        for url in scan_list:
            print (url)
        pass

    # Perform a search using a previously scanned url
    elif x == '3':
        url = fetch_from_db.get_url_list()
        if url is None:
            scan_url.scan_url(url)

    # Reset the database
    elif x == "4":
        x = input((print("Are you sure? (y/n)")))
        if x == "y":
            print("\nResetting databse...")
            build_db.reset_database()
            print("Database Reset.\n")
        main()

    elif x == "5":
        x = input(print("Are you sure?(y/n)"))
        if x == "y":
            build_db.reset_database()

    elif x == "9":
        quit()

    else:
        print("Invalid Input")
        main()

    build_db.close_database()


if __name__ == "__main__":
    main()
