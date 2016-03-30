
#!/usr/bin/env python2
#
# file:    message_generator.py
# authors: Nathan Burgers
# purpose: Provide a mechanism for getting a generator from an OutChannel
#

from channel import Channel

def MessageGenerator(out_channel):
    """
    Create a generator that infinitely iterates the messages from an OutChannel
    :param out_channel: The OutChannel to receive messages from
    :return:            The infinite generator of messages from 'out_channel'
    """
    while True:
        yield out_channel.receive()
