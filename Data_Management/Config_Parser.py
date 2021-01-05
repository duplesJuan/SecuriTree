import configparser


def return_config_as_dict(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    conf_vars = {'db_host': config['db_credentials']['host'],
                 'db_username': config['db_credentials']['username'],
                 'db_password': config['db_credentials']['password'],
                 'db_schema': config['db_credentials']['schema']}

    return conf_vars

