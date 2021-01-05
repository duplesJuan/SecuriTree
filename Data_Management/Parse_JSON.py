import json
import sys
import os


def get_Json(input_file):
    """
    This function takes in the path to the json file and returns the contents as a dictionary
    """
    try:
        with open(input_file, "r") as file:
            new_dict = json.loads(file.read())
    except FileNotFoundError:
        print("Cannot read input file!")
    finally:
        file.close()
        return new_dict


if __name__ == '__main__':
    print(get_Json(r"../Import_data/registered_users.json"))

