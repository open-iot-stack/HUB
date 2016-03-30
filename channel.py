#
# file:   channel.py
# author: Nathan Burgers
#

from Queue import Queue
from Queue import Empty

class SendException(Exception):
    """
    SendException is a value-semantic class that indicates an attempt to
    send a message to an InChannel with a full message queue
    """
    pass

class InChannel(object):
    """
    InChannel is a mechanism class intended to be created by the Channel
    class.  InChannel is thread safe.
    """
    def __init__(self, concurrent_queue):
        """
        Construct a new InChannel
        :param concurrent_queue: The queue from which to send messages
        :return:                 Nothing
        """
        self.queue = concurrent_queue

    def send_exn(self, message):
        """
        Send a message to the paired 'OutChannel' and raise a 'SendException'
        if the underlying message queue is full.
        :return: Nothing
        """
        try:
            self.queue.put_nowait(message)
        except Full:
            raise SendException

    def send(self, message):
        """
        Send a message to the paired 'OutChannel' and block until the
        underlying message queue has space for the message.
        :return: Nothing
        """
        self.queue.put(message, True, None)

class ReceiveException(Exception):
    """
    ReceiveException is a value-semantic class that indicates an attempt to
    receive a message from an OutChannel with an empty message queue.
    """
    pass

class OutChannel(object):
    """
    OutChannel is a mechanism class intended to be created by the Channel
    class.  OutChannel is thread safe.
    """
    def __init__(self, concurrent_queue):
        """
        Construct a new OutChannel
        :param concurrent_queue: The queue from which to receive messages
        :return:                 Nothing
        """
        self.queue = concurrent_queue

    def receive_exn(self):
        """
        Receive a message from the underlying message queue and raise a
        'ReceiveException' if the underlying message queue is empty
        :return: The received message
        """
        try:
            return self.queue.get_nowait()
        except Empty:
            raise ReceiveException()

    def receive(self):
        """
        Receive a message from the underlying message queue and block until
        a message becomes available.
        :return: The received message
        """
        return self.queue.get(True, None)

class Channel(object):
    """
    Channel is utility class to create an InChannel and OutChannel pair, such
    that messages sent through the InChannel are received through the
    OutChannel
    Example Usage:
        from channel import Channel
        in_channel, out_channel = Channel() # create the linked channels
        in_channel.send("A String Message")
        message = out_channel.receive()
        print message                       # displays "A String Message"
    """
    def __new__(channel_class):
        concurrent_queue = Queue()
        in_channel       = InChannel(concurrent_queue)
        out_channel      = OutChannel(concurrent_queue)
        return (in_channel, out_channel)
