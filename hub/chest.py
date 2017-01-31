#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import _thread

class Chest(object):
    """Chest holds a lock and a dictionary of data.
    The lock should be aquired before doing anything
    with the data
    """

    def __init__(self):
        self.data = {}
        self.lock = _thread.allocate_lock()
