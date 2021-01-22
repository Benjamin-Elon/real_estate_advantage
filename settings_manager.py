import json
import os


def save_settings(settings):

    settings_list = dict()

    # check if file is emtpy
    with open("settings", "r") as fh:
        data = fh.read()

    # if empty, write settings to file before reading
    if len(data) == 0:
        with open("settings", "w") as fh:
            settings_desc = input("Enter a description for this search profile:\n")
            settings_list[settings_desc] = settings
            json.dump(settings_list, fh)
    # settings exist
    else:
        # get saved settings from file
        with open("settings", "r") as fh:
            js_data = json.load(fh)
            settings_desc = input("Enter a description for this search profile:\n")
            js_data[settings_desc] = settings
            print(js_data)
            fh.close()

        # Save the list of settings to file
        with open("settings", "w") as fh:
            json.dump(js_data, fh)

    fh.close()

    return


def load_settings():

    with open('settings', 'r') as fh:
        contents = fh.readlines()
        fh.close()

    if contents:
        with open('settings', 'r') as fh:
            settings = json.load(fh)
        selection_list = list()
        x = 0
        for key, value in settings.items():
            print("(", x, ")", key, value)
            x += 1
            selection_list.append(value)

        try:
            selection = int(input("Select an option:\n"))
            settings = selection_list[selection]
        except (ValueError, IndexError):
            print("Invalid selection.")
            settings = load_settings()

        # extract selection from settings dict
        settings = list(settings.values())[0]
        return settings

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
