# SecuriTree
This repo contains the code for the SecuriTree Access Management Application

This application handles all of the backend set up on its own. 
Please note that a MYSQL server instance should be installed and running on the user PC. 
The credentials for the DB should be set up by the user in the config.ini file.

The business logic is mostly based in Python 3.6.

Python Requirements are (however most are part of the Python Standard library) -
* getpass
* os
* pymysql
* sys
* hashlib
* binascii
* configparser
* json

### Steps To Set Up Application
1. Ensure that you have MYSQL Server installed (can be downloaded from [here](https://dev.mysql.com/downloads/))
2. Open the config.ini file and fill in the database credentials. 
    * host - if MYSQL is installed on your local pc, host will likely be set to 'localhost' unless set up otherwise.
    * username and password - will be the same as credentials for your MYSQL Server.
    * schema - will be the database name for your security system (if it does not exist, it will be created automatically with the database initialisation step)
3. Run the Initiate_DB.py file to create and populate the database with the data needed for the Access Management Application. **Note** -  the user passwords are hashed for secure storing in a database
4. You can now run the Access Management Application

### Application Workflow
1. Login using the authorised username and password to access the Access Management System
2. Select to either - 
    * View the access hierarchy or
    * Manage the doors
    
    ![main menu](https://github.com/duplesJuan/SecuriTree/blob/master/Images/main_menu.jpg?raw=true)
3. The view access hierarchy option allows the user to see the status of all the doors in the building as well as the access rules for the areas in a hierarchical structure.

    ![hierarchy](https://github.com/duplesJuan/SecuriTree/blob/master/Images/hierarchy.jpg?raw=true)
