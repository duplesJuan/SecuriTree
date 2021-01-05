import pymysql
import hashlib
import os
import binascii
import Parse_JSON
import Config_Parser as cfg


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


if __name__ == '__main__':
    conf_vars = cfg.return_config_as_dict(r"..\config.ini")
    db = pymysql.connect(conf_vars["db_host"],
                         conf_vars["db_username"],
                         conf_vars["db_password"])
    cursor = db.cursor()

    # This checks to see if an appropriate db already exists and creates one if not
    cursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(conf_vars["db_schema"]))
    # This checks to see if an appropriate table already exists for users and creates one if not
    cursor.execute("CREATE TABLE IF NOT EXISTS {}.AUTH_USERS (username VARCHAR(100), first_name VARCHAR(100), surname VARCHAR(100), password VARCHAR(1000));".format(conf_vars["db_schema"]))
    # This checks to see if an appropriate table already exists for areas and creates one if not
    cursor.execute("CREATE TABLE IF NOT EXISTS {}.AREAS (id VARCHAR(100), name VARCHAR(100), parent_area_id VARCHAR(1000), child_area_ids VARCHAR(1000));".format(conf_vars["db_schema"]))
    # This checks to see if an appropriate table already exists for doors and creates one if not
    cursor.execute("CREATE TABLE IF NOT EXISTS {}.DOORS (id VARCHAR(100), name VARCHAR(100), parent_area VARCHAR(1000), status VARCHAR(10));".format(conf_vars["db_schema"]))
    # This checks to see if an appropriate table already exists for access rules and creates one if not
    cursor.execute("CREATE TABLE IF NOT EXISTS {}.ACCESS_RULES (id VARCHAR(100), name VARCHAR(100), doors VARCHAR(5000));".format(conf_vars["db_schema"]))

    # This prepares the data in dictionaries
    user_entries = Parse_JSON.get_Json(r"../Import_data/registered_users.json")["registered_users"]
    sys_data_areas_entries = Parse_JSON.get_Json(r"../Import_data/system_data.json")["system_data"]["areas"]
    sys_data_doors_entries = Parse_JSON.get_Json(r"../Import_data/system_data.json")["system_data"]["doors"]
    sys_data_acc_rules_entries = Parse_JSON.get_Json(r"../Import_data/system_data.json")["system_data"]["access_rules"]

    # This loads the userdata into the correct table
    count = 1
    for entry in user_entries:
        print("Importing user {} of {}".format(count,
                                               len(user_entries)))
        cursor.execute("""INSERT INTO {}.auth_users (username,first_name,surname,password)
                          select '{}','{}','{}','{}' from dual
                          where not exists (select * from securitree.auth_users where username = '{}' LIMIT 1);""".format(conf_vars["db_schema"],
                                                                                                                          entry["username"],
                                                                                                                          entry["first_name"],
                                                                                                                          entry["surname"],
                                                                                                                          hash_password(entry["password"]),
                                                                                                                          entry["username"]))
        count += 1
    db.commit()

    # This loads the areas data into the correct table
    count = 1
    for entry in sys_data_areas_entries:
        print("Importing area {} of {}".format(count,
                                               len(sys_data_areas_entries)))
        cursor.execute("""INSERT INTO {}.areas (id,name,parent_area_id,child_area_ids)
                          select '{}','{}','{}','{}' from dual
                          where not exists (select * from securitree.areas where id = '{}' LIMIT 1);""".format(conf_vars["db_schema"],
                                                                                                               entry["id"],
                                                                                                               entry["name"],
                                                                                                               entry["parent_area"],
                                                                                                               ";".join(entry["child_area_ids"]),
                                                                                                               entry["id"]))
        count += 1
    db.commit()

    # This loads the doors data into the correct table
    count = 1
    for entry in sys_data_doors_entries:
        print("Importing door {} of {}".format(count,
                                               len(sys_data_doors_entries)))
        cursor.execute("""INSERT INTO {}.doors (id,name,parent_area,status)
                          select '{}','{}','{}','{}' from dual
                          where not exists (select * from securitree.areas where id = '{}' LIMIT 1);""".format(conf_vars["db_schema"],
                                                                                                               entry["id"],
                                                                                                               entry["name"],
                                                                                                               entry["parent_area"],
                                                                                                               entry["status"],
                                                                                                               entry["id"]))
        count += 1
    db.commit()

    # This loads the access rules data into the correct table
    count = 1
    for entry in sys_data_acc_rules_entries:
        print("Importing access rule {} of {}".format(count,
                                                      len(sys_data_acc_rules_entries)))
        cursor.execute("""INSERT INTO {}.access_rules (id,name,doors)
                          select '{}','{}','{}' from dual
                          where not exists (select * from securitree.areas where id = '{}' LIMIT 1);""".format(conf_vars["db_schema"],
                                                                                                               entry["id"],
                                                                                                               entry["name"],
                                                                                                               ';'.join(entry["doors"]),
                                                                                                               entry["id"]))
        count += 1
    db.commit()

    db.close()
