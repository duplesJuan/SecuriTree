import getpass
import os
import pymysql
import sys
import hashlib
import binascii

import Config_Parser as cfg

tab = 0


def print_application_name():
    """This function prints the application name wherever necessary in the menus"""

    print("*************************************************\n"
          "*        SECURITREE - Security Dashboard        *\n"
          "*************************************************\n")


def login_dialogue():
    """This function displays the landing menu where the
    user is initially asked to log in"""

    print_application_name()
    print("Welcome to Securitree! \n"
          "\n"
          "Please enter your login credentials to begin."
          "")
    user = input("Username: ")
    passwd = getpass.getpass("Password: ")

    return user, passwd


def try_again_dialogue():
    """This function displays the screen when the log in
    attempt was unsuccessful and prompts the user to try again"""

    print_application_name()
    print("Login failed. \n"
          "\n"
          "Please enter your login credentials to try again."
          "")
    user = input("Username: ")
    passwd = getpass.getpass("Password: ")

    return user, passwd


def check_auth_login(user, passwd):
    """This function checks to see if the user trying to log in is authorised to do so"""

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT * FROM {}.auth_users WHERE username = '{}';".format(conf_vars["db_schema"],
                                                                               user))
    if cursor.rowcount == 1:
        for row in cursor:
            if verify_password(row[3], passwd):
                return True
            else:
                return False
    else:
        return False


def show_main_menu_dialogue():
    """This function prints the main menu dialogue to the user"""

    print_application_name()
    print("Main Menu Options:\n"
          "1. View Security Entity Hierarchy\n"
          "2. Manage Doors\n"
          "3. Log Out\n")
    menu_selection = input("Option: ")

    if menu_selection == '1':
        clear_screen()
        show_security_hierarchy()
    elif menu_selection == '2':
        clear_screen()
        show_manage_doors_screen()
    elif menu_selection == '3':
        clear_screen()
        show_logged_out_screen()
        clear_screen()
        handle_login()


def show_logged_out_screen():
    """This function displays the logged out screen when the user opts to log out"""

    print_application_name()
    input("You have logged out! Press ENTER to login.\n")


def show_security_hierarchy():
    """This function displays the screen that shows the security hierarchy"""

    print_application_name()
    print("Entity Hierarchy:\n\n")

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT id, name, parent_area_id, child_area_ids FROM {}.areas where parent_area_id = \'None\'".format(conf_vars["db_schema"]))

    for row in cursor:
        read_recursive_area_hierarchy(row[0])

    print("\nPress ENTER to return to the main menu.")
    pause = input()
    clear_screen()
    show_main_menu_dialogue()


def read_recursive_area_hierarchy(id, tab=''):
    """This function reads recursively into the area hierarchy and
    subsequently displays all the relevant info such as the doors and the access rules"""

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT id, name, parent_area_id, child_area_ids FROM {}.areas where id = \'{}\'".format(conf_vars["db_schema"],
                                                                                                            id))
    for row in cursor:
        print(tab + '\- ' + row[1])
        tab = tab + '\t'
        print(tab + display_door_information(row[0]))
        print(tab + display_access_rules(row[0]))
        for child_area in row[3].split(";"):
            read_recursive_area_hierarchy(child_area, tab=tab)


def display_access_rules(parent_area_id):
    """This function formats the access rules information into one string
    for a specific area"""

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT id, name, parent_area, status FROM {}.doors where parent_area = \'{}\'".format(conf_vars["db_schema"],
                                                                                                          parent_area_id))
    doors = []
    access_rules = set()
    access_rules_string = '|- [Access Rules] '
    for row in cursor:
        doors.append(row[0])

    cursor.execute("SELECT id, name, doors FROM {}.access_rules".format(conf_vars["db_schema"]))
    for row in cursor:
        for door in doors:
            if door in row[2]:
                access_rules.add(row[1])

    count = 1
    for rule in access_rules:
        if count == len(access_rules):
            access_rules_string += rule
        else:
            access_rules_string += rule + ', '
        count += 1

    return access_rules_string


def display_door_information(id):
    """This function formats the door information into one string for a specific area"""

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT id, name, parent_area, status FROM {}.doors where parent_area = \'{}\'".format(conf_vars["db_schema"],
                                                                                                          id))
    door_string = '|- [Doors] '

    count = 1
    for row in cursor:
        if row[3] == 'open':
            CSTR = '\033[92m'
        else:
            CSTR = '\033[91m'
        CEND = '\033[0m'

        if cursor.rowcount == count:
            door_string += row[1] + ' (' + CSTR + row[3].upper() + CEND + ')'
        else:
            door_string += row[1] + ' (' + CSTR + row[3].upper() + CEND + '), '
        count += 1
    return door_string


def show_manage_doors_screen():
    """This function prints the manage doors dialogue to the user"""

    print_application_name()
    print("Manage Doors Menu Options:\n"
          "1. Lock Door\n"
          "2. Unlock Door\n"
          "3. List Door IDs\n"
          "4. Back\n")
    menu_selection = input("Option: ")

    if menu_selection == '1':
        clear_screen()
        show_lock_unlock_screen('l')
    elif menu_selection == '2':
        clear_screen()
        show_lock_unlock_screen('u')
    elif menu_selection == '3':
        clear_screen()
        list_door_ids()
    elif menu_selection == '4':
        clear_screen()
        show_main_menu_dialogue()


def list_door_ids():
    """This function prints the screen showing the
    doornames and ids for use in the lock and unlock system"""

    print_application_name()

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()
    cursor.execute("SELECT id, name, status FROM {}.doors".format(conf_vars["db_schema"]))
    print ("{:<30}\t{:<36}\t{}".format("Name",
                                       "ID",
                                       "Status"))
    for row in cursor:
        if row[2] == 'open':
            CSTR = '\033[92m'
        else:
            CSTR = '\033[91m'
        CEND = '\033[0m'
        print("{:<30}\t{:<36}\t{}{}{}".format(row[1],
                                              row[0],
                                              CSTR,
                                              row[2],
                                              CEND))

    pause = input("\nPress ENTER to return to the door management menu")
    clear_screen()
    show_manage_doors_screen()


def show_lock_unlock_screen(action):
    """This function prints the manage doors dialogue to the user"""

    print_application_name()
    if action == 'l':
        print("Lock Door\n\n"
              "Please enter the ID of the door to lock or type 0 to go back.\n")
    elif action == 'u':
        print("Unlock Door\n\n"
              "Please enter the ID of the door to unlock or type 0 to go back.\n")
    door_id = input("Door ID: ")

    if len(door_id) == 1:
        clear_screen()
        show_manage_doors_screen()

    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"],
                         conf_vars["db_schema"])
    cursor = db.cursor()

    if action == 'l':
        cursor.execute("UPDATE {}.doors set status = \'closed\' where id = \'{}\';".format(conf_vars["db_schema"],
                                                                                           door_id))
    elif action == 'u':
        cursor.execute("UPDATE {}.doors set status = \'open\' where id = \'{}\';".format(conf_vars["db_schema"],
                                                                                         door_id))
    db.commit()

    clear_screen()
    print_application_name()
    if action == 'l':
        print("Door {} locked!\n"
              "Press ENTER to return to the main menu".format(door_id))
    elif action == 'u':
        print("Door {} unlocked!\n"
              "Press ENTER to return to the main menu".format(door_id))
    pause = input()
    clear_screen()
    show_main_menu_dialogue()


def clear_screen():
    """This function clears the screen to facilitate menu movement"""

    clear = lambda: os.system('cls')
    clear()


def handle_login():
    clear_screen()
    user, password = login_dialogue()
    logged_in = check_auth_login(user, password)

    while not logged_in:
        clear_screen()
        user, password = try_again_dialogue()
        logged_in = check_auth_login(user, password)

    if logged_in:
        clear_screen()
        show_main_menu_dialogue()


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


if __name__ == "__main__":
    conf_vars = cfg.return_config_as_dict(sys.argv[1])
    handle_login()
