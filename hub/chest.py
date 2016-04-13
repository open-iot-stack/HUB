#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import thread

class Chest(object):
    """Chest holds a lock and a dictionary of data. 
    The lock should be aquired before doing anything
    with the data
    """

    data = {}
    lock = thread.allocate_lock()
