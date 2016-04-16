#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import thread

class Config():
    """Config is a class that will be able to interact with 
    the configuration. This is to add an API layer for the
    config implementation"""

    _fpath = ".config" # file path of the config file
    _flock = thread.allocate_lock() # file lock in case shared across threads
    _modified = True
    _cache = {}

    def __init__(self, fpath=None):
        """TODO: to be defined1. """
        if fpath:
            self._fpath = fpath

    def set_path(self, fpath):
        """Clears the cache and sets a new file for the config
        :fpath: new filepath for the new Config object
        :returns: boolean on if new config file exists
        """

        assert(type(fpath) == str)
        self._fpath = fpath
        self._modified = True
        self._cache = {}
        return self.load_data()

    def load_data(self):
        """Loads data from file into cache. Happens on read_data as
        well but can be called earlier to make sure it's loaded in
        the future. If the config file is not found, return false
        :returns: boolean on success/failure
        """
        u_types = {}
        with self._flock:
            if not os.path.isfile(self._fpath):
                return False
            with open(self._fpath, 'r') as f:
                lines = f.readlines()
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
                uuid = int(uuid)
                u_types[uuid] = chip_type
        self._cache = u_types
        self._modified = False
        return True

    def read_data(self):
        """Returns a dictionary list of UUIDs and Types
        Should be used everytime data is accessed for most
        up to date data.

        :returns: dictionary of uuid and types
        """
        u_types = {}
        with self._flock:
            if  self._modified == False:
                return self._cache
            if not os.path.isfile(self._fpath):
                return {}
            with open(self._fpath, 'r') as f:
                lines = f.readlines()
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
                uuid = int(uuid)
                u_types[uuid] = chip_type
        self._cache = u_types
        self._modified = False
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
        with self._flock:
            self._modified = True
            with open(self._fpath, "a+") as f:
                for key,value in data.items():
                    f.write(str(key) + " " + value + "\n")
        return True

    def update_data(self, data):
        """Update the config with all UUIDs in data. Fails if
        a key doesn't exist

        :data: TODO
        :returns: TODO
        """

        with self._flock:
            self._modified = True
            with open(self._fpath, "r") as f:
                lines = f.readlines()
            new_lines = []
            for i in range(len(lines)):
                if (lines[i].startswith("#")):
                    new_lines.append(lines[i])
                elif (lines[i].startswith("\n")):
                    pass
                else:
                    uuid, chip_type = lines[i].replace('\n', '').split(" ")
                    uuid = int(uuid)
                    if data.has_key(uuid):
                        new_lines.append(str(uuid) + " " + data[uuid] + "\n")
                        data.pop(uuid)
                    else:
                        new_lines.append(lines[i])
            if len(data) > 0:
                return False

            with open(self._fpath, "w") as f:
                f.writelines(new_lines)
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
    #print str(config.read_data())
    print config.load_data()
    print config.add_data({"21513": "camera"})
    print str(config.read_data())
    print config.add_data({"21141": "camera"})
    print str(config.read_data())
    print str(config.read_data())
    print config.add_data({"21141": "temperature"})
    print str(config.read_data())
    print config.add_data({"13513": "time"})
    print str(config.read_data())
    print config.update_data({"21513": "temperature"})
    print str(config.read_data())
    print config.add_data({"21212": "camera"})
    print config.update_data({"21212": "temperature"})
    print str(config.read_data())
