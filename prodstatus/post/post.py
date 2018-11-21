#!/bin/python
import json
import requests
import sys
import os
try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse


def posthelp():
    print("python post.py <json-filename> <url>")
    print("python post.py my.json http://127.0.0.1:9191/upload")
    sys.exit(1)

def main(url, path):
    """
    :url: String
    :path: String
    """
    try:
        with open(path, "r") as data_file:
            data = json.load(data_file)
    except:
        print("failed to load {}".format(path))
        sys.exit(1)

    r = requests.post(url, json=data)
    print("status_code: {}".format(r.status_code))

def is_url(url):
    """
    :url: String
    :return: Bool
    """
    try:
        result=urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        posthelp()

    path = os.path.join(os.path.abspath('.'), sys.argv[1])
    url = sys.argv[2]

    print("looking for {}".format(path))
    if not os.path.isfile(sys.argv[1]):
        print("{} not found".format(path))
        sys.exit(2)

    print("controlling url: {}".format(url))
    if not is_url(url):
        print("invalid url: {}".format(url))
        sys.exit(3)

    main(url, path)
