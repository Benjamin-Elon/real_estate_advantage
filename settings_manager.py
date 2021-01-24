import json
import os


def save_settings(cur_settings):

    settings_list = dict()

    if not os.path.exists("settings"):
        with open("settings", "w+") as fh:
            fh.close()

    # check if file is emtpy
    with open("settings", "r") as fh:
        data = fh.read()

    # if empty, write settings to file before reading
    if len(data) == 0:
        with open("settings", "w") as fh:
            settings_desc = input("Enter a description for this search profile:\n")
            settings_list[settings_desc] = cur_settings
            json.dump(settings_list, fh)

    # settings exist
    else:
        # get saved settings from file
        with open("settings", "r") as fh:
            settings = json.load(fh)
            settings_desc = input("Enter a description for this search profile:\n")
            settings[settings_desc] = cur_settings
            # print(settings)
            for key, value in settings.items():
                print(key, value)

            fh.close()

        # Save the list of settings to file
        with open("settings", "w") as fh:
            json.dump(settings, fh)

    fh.close()

    return

# https://www.yad2.co.il/realestate/rent?area=20
# https://www.yad2.co.il/realestate/rent?area=74
# https://www.yad2.co.il/realestate/rent?area=83
# https://www.yad2.co.il/realestate/rent?topArea=101
# https://www.yad2.co.il/realestate/rent?area=21
# https://www.yad2.co.il/realestate/rent?area=22


def load_settings():

    with open('settings', 'r') as fh:
        contents = fh.readlines()
        fh.close()

    if contents:
        with open('settings', 'r') as fh:
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

    if os.path.exists("settings"):
        os.remove("settings")
        print("Settings deleted successfully.\n")
    else:
        print("Settings file does not exist.\n")

    with open("settings", "w+") as fh:
        fh.close()

    return
