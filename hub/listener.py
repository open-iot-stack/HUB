#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import threading

class Listener(object):

    """Listener object. Holds information about threads related to a id"""

    def __init__(self):
        self.threads = {}
        self.lock    = threading.Lock()

    def is_alive(self, id):
        return (id in self.threads and self.threads[id].is_alive())

    def add_thread(self, id, thread):
        """Will attempt to add a thread for a given id
        :id: id of object to assign the thread
        :thread: thread object
        :returns: Boolean of success, fails if id has a living thread

        """
        assert(isinstance(thread, threading.Thread))
        with self.lock:
            if self.is_alive(id):
                return False
            self.threads[id] = thread
            return True

