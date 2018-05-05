#!/usr/bin/python
"""
server
"""
import socket, fcntl, struct
import logging
import json
import os
import sys
import pymssql
from flask import Flask, jsonify, render_template,\
    request, send_from_directory, send_file
import ConfigParser
import ast

APP = Flask(__name__, static_url_path='')

CONN = None
CURSOR = None

# LOGGING CONFIGURATION
FORMAT = '%(asctime)-30s %(levelname)-10s ' +\
        '[%(filename)-20s %(funcName)25s()] ' +\
        '%(message)s'
logging.basicConfig(filename="serve.log", level=logging.INFO, format=FORMAT)
logging.getLogger().addHandler(logging.StreamHandler())

NODES={}

"""-------------------------------------------------"""
@APP.route('/upload', methods=['POST'])
def supply_data():
    """
    supply packet information with airtimes.
    :return: json
    """
    global NODES
    global CURSOR
    global CONN
    data = ast.literal_eval(request.get_json())
    val = data['barcode']
    val = val.replace("=","-")

    if NODES['start'] == request.remote_addr:
        print("production started for {}".format(val))
        # query = "SELECT * FROM dbo.LG_103_PRODORD WHERE FICHENO='{}'".format(val)
        query = "UPDATE dbo.LG_103_PRODORD SET STATUS=0 WHERE FICHENO='{}'".format(val)
        print(query)
        CURSOR.execute(query)
    elif NODES['finish'] == request.remote_addr:
        print("production finished for {}".format(data))
        # query = "SELECT * FROM dbo.LG_103_PRODORD WHERE FICHENO='{}'".format(val)
        query = "UPDATE dbo.LG_103_PRODORD SET STATUS=0 WHERE FICHENO='{}'".format(val)
        print(query)
        CURSOR.execute(query)
    else:
        print("dont know the node {}".request.remote_addr)
    CONN.commit()
    return jsonify(result="abc")

#   -------------------------------------------------

def get_interface_ip(ifname):
    """ip address of interface
    :ifname: str
    :return: str
    This function gets IP addr of interface
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(sock.fileno(),\
            0x8915, struct.pack('256s', ifname[:15]))[20:24])

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
        print('Could not parse:', err)
        return None

    for elem in sections:
        for name, value in parser.items(elem):
            config[name] = value

    return config

def main():
    """main func"""
    global NODES 
    global CURSOR
    global CONN
    config = get_config("config.ini", ["server"])
    NODES = get_config("config.ini", ["nodes"])

    CONN = pymssql.connect(host='10.0.0.2', user='kivanc',
            password='selen30031994', database='LKSDB', timeout=10)
    CURSOR=CONN.cursor()

    APP.run(
            host=get_interface_ip(config['interface']),
            port=int(config['port']),
            debug=True
            )

if __name__ == "__main__":
    main()
