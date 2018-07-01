#!/usr/bin/python
"""
client scripts to update remote Microsoft SQL Server 
w.r.t barcode device interrupts.
"""

from evdev import InputDevice, ecodes, list_devices, categorize
import os
import signal, sys
import pymssql
import ConfigParser
import logging
from constants import Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler(os.path.abspath('client.log'))
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

logger.info('Starting')

def signal_handler(signal, frame):
    logger.warn('Stopping')
    dev.ungrab()
    sys.exit(0)

#TODO: check more advanced API of ConfigParser
def get_config(cfile, sections):
    """read config.ini which contains required meta-data
    to serve UI, relative paths of raw/processed data,
    server configuration.
    :cfile: Str[]
    :sections: Str[]
    :return: dict
        configuration
    """
    pack_info, config = {}, {}
    try:
        parser = ConfigParser.SafeConfigParser()
        parser.read(cfile)
    except ConfigParser.ParsingError, err:
        logger.error('Could not parse:', err)
        return None

    if type(sections) is list:
        for elem in sections:
            for name, value in parser.items(elem):
                config[name] = value
    elif type(sections) is str:
        for name, value in parser.items(sections):
            config[name] = value

    return config

def record_status(barcode, config, cursor):
    """
    :barcode: Str
    :config: dict
    :cursor: sql connection token
    """
    cmd = config['cmd'].format(
            config['status'], barcode)
    logger.info(cmd)
    cursor.execute(cmd)

def task_loop(dev, cursor, conn, config):
    """reads barcode and updates sql database
    :dev: InputDevice
    :cursor: sql connection token
    :config: dict
    """
    barcode = ""
    scancodes = Constants.scancodes()
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            # Catch only keydown, and not Enter
            if data.keystate == 1 and data.scancode != 42:
                if data.scancode == 28:
                    barcode = barcode.replace("=", "-")
                    record_status(barcode, config, cursor)
                    conn.commit()
                    logger.info(barcode)
                    barcode = ""
                else:
                    barcode += scancodes[data.scancode]

def get_device(dev_name):
    """
    :dev_name: String
    :return: InputDevice
        None in failure
    """
    dev = None
    devices = map(InputDevice, list_devices())

    for device in devices:
        logger.info(device.name)
        if dev_name.lower() in device.name.lower():
            logger.info('found device')
            return InputDevice(device.fn)
    return dev

def db_connect(host, user, password,
        database, query_timeout, login_timeout):
    """
    :host: String
    :user: String
    :password: String
    :database: String
    :query_timeout: int
    :login_timeout: int
    :return: connection token
    """
    logger.info("trying to connect, timeout: {}".format(login_timeout))
    try:
        conn = pymssql.connect(host=host,
                user=user, password=password,
                database=database,
                timeout=query_timeout,
                login_timeout=login_timeout)
    except pymssql.OperationalError, err:
        logger.error('failed to connect:', err)
        return None
    logger.info('connected')
    return conn

def conn_check(ip_addr):
    """
    :ip_addr: String
    """
    while True:
        response = os.system('ping -c 1 {}'.format(ip_addr))
        if response == 0:
            return
        logger.warn('no connection, re-try')
        time.sleep(1)

def main():
    """main block
    get barcode scanner device
    connect to sql database
    start task loop
    """
    cursor, dev = None, None
    signal.signal(signal.SIGINT, signal_handler)
    conf_path = os.path.abspath(Constants.config_file())
    config = get_config(conf_path,
            Constants.config_sections())
    conn_check(config['host'])

    dev = get_device(config['dev_name'])
    if not dev:
        logger.error("failed to find {}".format(config['dev_name']))
        sys.exit(1)
    dev.grab()

    conn = db_connect(config['host'], config['user'],
            config['password'], config['database'],
            config['query_timeout'], config['login_timeout'])
    if conn == None:
        logger.info("failed to connect to db")
        sys.exit(2)
    cursor = conn.cursor()

    logger.info('entering task loop')
    task_loop(dev, cursor, conn, config)

if __name__ == "__main__":
    main()
