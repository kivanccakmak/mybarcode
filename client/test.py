import os          
import sys
import pymssql
import ConfigParser
from constants import Constants
from client import get_config
from client import db_connect
from client import record_status

def query_status(barcode, config, cursor):
    """
    :barcode: Str
    :config: dict
    :cursor: sql connection token
    """
    cmd = config['cmd_query'].format(barcode)
    try:
        cursor.execute(cmd)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        msg = ''.join('!! ' + line for line in lines)
        logging.error(msg)
    res = cursor.fetchone()
    print(res)

def main(barcode, status):
    """
    :barcode: String
    :status: String
    """
    conf_path = os.path.abspath(Constants.config_file())
    config = get_config(conf_path, Constants.config_sections())
    conn = db_connect(config['host'], config['user'], config['password'], 
            config['database'], config['query_timeout'], 
            config['login_timeout'])
    record_status(barcode, config, cursor)
    conn.commit()

if __name__ == "__main__":
    if len(sys.argv) is not 3:
        print("invalid usage")
        print('python test.py barcode status')
        print('python test.py 1612-1 "Dvm Ediyor"')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
