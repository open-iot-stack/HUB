#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import threading

class Config():
    """Config is a class that will be able to interact with 
    the configuration. This is to add an API layer for the
    config implementation"""

    _fpath = "config/test.config" # file path of the config file
    _flock = threading.Lock() # file lock to in case shared across threads
    _modified = True
    _cache = {}

    def __init__(self):
        """TODO: to be defined1. """

    def set_config(self, fpath):
        """Creates a new Config object with fpath as it's config file

        :fpath: new filepath for the new Config object
        :returns: new Config object
        """

        assert(type(fpath) == str)
        new_config = Config()
        new_config._fpath = fpath
        return new_config

    def read_data(self):
        """Returns a dictionary list of UUIDs and Types
        Should be used everytime data is accessed for most
        up to date data.

        :returns: dictionary of uuid and types
        """
        u_types = {}
        self._flock.acquire()
        f = open(self._fpath, "r")
        last_modified = os.path.getmtime(self._fpath)
        if  self._modified == False:
            f.close()
            self._flock.release()
            return self._cache
        lines = f.readlines()
        self._modified = False
        self._cache = u_types
        f.close()
        self._flock.release()
        for line in lines:
            if line.startswith("#"):
                pass
            elif line.startswith("\n"):
                pass
            else:
                try:
                    uuid, chip_type = line.replace('\n', '').split(" ")
                except ValueError:
                    print "Too many spaces in config file, please check", fpath
                    exit()
                u_types[uuid] = chip_type
        return u_types

    def add_data(self, data):
        """Append data to the config file. The data should be in
        a dictionary format. Key: UUID, value: Type. If a key exists,
        it does not update an entry and will return false.

        :data: dictionary to add to the config storage
        :returns: boolean on success/failure
        """
        assert(type(data) == dict)
        prev_data = self.read_data()
        # if there are multiple keys, fail
        if (len(dict_shared(prev_data, data)) != 0):
            return False
        self._flock.acquire()
        self._modified = True
        f = open(self._fpath, "a")
        for key,value in data.items():
            f.write(key + " " + value + "\n")
        f.close()
        self._flock.release()
        return True

    def update_data(self, data):
        """Update the config with all UUIDs in data. Fails if
        a key doesn't exist

        :data: TODO
        :returns: TODO
        """

        self._flock.acquire()
        self._modified = True
        f = open(self._fpath, "r+")
        lines = f.readlines()
        new_lines = []
        for i in range(len(lines)):
            if (lines[i].startswith("#")):
                new_lines.append(lines[i])
            elif (lines[i].startswith("\n")):
                pass
            else:
                uuid, chip_type = lines[i].replace('\n', '').split(" ")
                if data.has_key(uuid):
                    new_lines.append(uuid + " " + data[uuid] + "\n")
                    data.pop(uuid)
                else:
                    new_lines.append(lines[i])
        if len(data) > 0:
            f.close()
            self._flock.release()
            return False

        f.seek(0)
        f.writelines(new_lines)
        f.close()
        self._flock.release()
        return True

def dict_shared(dict1, dict2):
    """Returns a list of keys that are shared
    between two dictionaries

    :dict1: TODO
    :dict2: TODO
    :returns: TODO
    """

    l = []
    assert(type(dict1) == dict)
    assert(type(dict2) == dict)
    for key in dict1.keys():
        if dict2.has_key(key):
            l.append(key)
    return l

if __name__ == '__main__':
    config = Config()
    print str(config.read_data())
    print config.add_data({"21513": "cam"})
    print str(config.read_data())
    print config.add_data({"21141": "cam"})
    print str(config.read_data())
    print str(config.read_data())
    print config.add_data({"21141": "temp"})
    print str(config.read_data())
    print config.add_data({"13513": "time"})
    print str(config.read_data())
    print config.update_data({"21513": "temp"})
    print str(config.read_data())
    print config.add_data({"21212": "cam"})
    print config.update_data({"21212": "temp"})
    print str(config.read_data())
