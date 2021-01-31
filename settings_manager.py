import json
import os


def save_settings(cur_settings, filename):
    filename = 'Settings/' + filename
    settings_list = dict()

    if not os.path.exists(filename):
        with open(filename, "w+") as fh:
            fh.close()

    # check if file is emtpy
    with open(filename, "r") as fh:
        data = fh.read()

    # if empty, write settings to file before reading
    if len(data) == 0:
        with open(filename, "w") as fh:
            settings_desc = input("Enter a description for this search profile:\n")
            settings_list[settings_desc] = cur_settings
            json.dump(settings_list, fh)

    # settings exist
    else:
        # get saved settings from file
        with open(filename, "r") as fh:
            settings = json.load(fh)
            settings_desc = input("Enter a description for this search profile:\n")
            settings[settings_desc] = cur_settings
            # print(settings)
            for key, value in settings.items():
                print(key, value)

            fh.close()

        # Save the list of settings to file
        with open(filename, "w") as fh:
            json.dump(settings, fh)

    fh.close()

    return


def load_settings(filename):
    filename = 'Settings/' + filename

    if not os.path.exists(filename):
        with open(filename, "w+") as fh:
            fh.close()

    with open(filename, 'r') as fh:
        contents = fh.readlines()
        fh.close()

    if contents:
        with open(filename, 'r') as fh:
            settings = json.load(fh)
        selection_list = list()
        x = 0
        for item in settings:
            print("(", x, ")", item)
            x += 1
            selection_list.append(settings[item])

        while True:
            try:
                selection = int(input("Select an option:\n"))
                cur_settings = selection_list[selection]
                break
            except (ValueError, IndexError):
                print("Invalid selection.")

        return cur_settings

    else:
        print("No settings detected.")
        return None


def delete_settings():

    while True:
        x = input("Select settings to delete:\n"
                  "(1) Search urls\n"
                  "(2) Areas selection\n"
                  "(3) Apartment analysis profile\n"
                  "(9) Back to the main menu")
        if x == '1':
            filename = 'search_urls'
        elif x == '2':
            filename = 'areas_constraints'
        elif x == '3':
            filename = 'search_profile'
        else:
            print("Invalid selection...\n")
            continue
        break

    filename = 'Settings/' + filename

    x = input("Are you sure you want to delete " + filename + " Setting? (y/n)")
    if x == 'y':
        if os.path.exists(filename):
            os.remove(filename)
            print("Settings deleted successfully.\n")
        else:
            print("Settings file does not exist.\n")
    else:
        return

    with open(filename, "w+") as fh:
        fh.close()

    return
