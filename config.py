import configparser
import os

def db_config(filename='config.ini', section='Database'):
    # If filename is relative, resolve it from the repository root
    # (not from current working directory, which might be backend/)
    if not os.path.isabs(filename) and not os.path.exists(filename):
        # Try to find config.ini in parent directory (repo root)
        parent_path = os.path.join(os.path.dirname(__file__), '..', filename)
        if os.path.exists(parent_path):
            filename = parent_path
    
    config = configparser.ConfigParser()
    config.read(filename)
    
    return {
        'host' : config.get(section, 'host'),
        'port' : config.get(section, 'port'),
        'user' : config.get(section, 'user'),
        'password' : config.get(section, 'password'),
        'database' : config.get(section, 'database')
    }
