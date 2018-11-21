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

APP = Flask(__name__)

# LOGGING CONFIGURATION
FORMAT = '%(asctime)-30s %(levelname)-10s ' +\
        '[%(filename)-20s %(funcName)25s()] ' +\
        '%(message)s'
logging.basicConfig(filename="serve.log", level=logging.INFO, format=FORMAT)
logging.getLogger().addHandler(logging.StreamHandler())

"""-------------------------------------------------"""
@APP.route('/upload', methods=['POST'])
def supply_data():
    """
    supply packet information with airtimes.
    :return: json
    """
    print(request.json)
    return jsonify(result="abc")

@APP.route("/record.html")
def index():
    fd = open("/tmp/recordlock", "w")
    lock(fd)
    with open("data/record.json", "r") as data_file:
        data = json.load(data_file)
    unlock(fd)
    return render_template('record.html', 
            colnames=data['colnames'], 
            records=data['records'])

# -------------------------------------------------

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
    :sections: Str[] or Str
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

    if type(sections) is list:
        for elem in sections:
            for name, value in parser.items(elem):
                config[name] = value
    elif type(sections) is str:
        for name, value in parser.items(sections):
            config[name] = value

    return config

def lock(fd):
    """
    :fd: int
    """
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError as e:
            # raise on unrelated IOErrors
            if e.errno != errno.EAGAIN:
                raise
            else:
                time.sleep(0.1)

def unlock(fd):
    """
    :fd: int
    """
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    except:
        print("failed to unlock")

def main():
    """main func"""
    config = get_config("config.ini", ["server"])

    APP.run(
            host=get_interface_ip(config['interface']),
            port=int(config['port']),
            debug=True
            )

if __name__ == "__main__":
    main()
