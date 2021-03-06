"""
    Client/Receiver.py
    ------------------

    This listens for incoming messages from the TroopServer

"""
from __future__ import absolute_import
from .threadserv import ThreadedServer
from .message import *
from .config import *

import socket
from threading import Thread
from time import sleep

class Receiver:
    """
        Listens for messages from a remote FoxDot Server instance
        and send keystroke data

    """

    def __init__(self, socket):

        self.sock = socket
        self.address = self.sock.getsockname()

        self.thread = Thread(target=self.handle)
        self.thread.daemon = True
        self.running = False
        self.bytes = 2048

        self.reader = NetworkMessageReader()

        # Information about other clients

        self.nodes = {}

        # Information about the text widget

        self.ui = None

    def __call__(self, client_id, attr):
        """ Returns the information about a connected client """
        return getattr(self.nodes[client_id], attr, None)

    def get_id(self):
        """ Returns the client_id nunmber for the local client """
        for node_id, node in self.nodes.items():
            if node == self.address:
                return node_id        

    def start(self):
        self.running = True
        self.thread.start()

    def kill(self):
        self.running = False
        self.sock.close()
        return

    def handle(self):
        
        while self.running:

            try:

                network_msg = self.reader.feed(self.sock.recv(self.bytes))

                if network_msg is None:

                    continue
                    
            except(OSError, socket.error) as e:

                # Connection lost errors - possible to reconnect?

                print(e)

                self.kill()

                break

            # Ignore empty message errors if we are no longer running

            except EmptyMessageError as e:

                if self.running:

                    raise(e)

                else:

                    pass

            for msg in network_msg:

                # Store address information about a newly connected client

                if isinstance(msg, MSG_CONNECT):

                    self.nodes[msg['src_id']] = Node(**msg.dict())

                self.update_text(msg)
                    
        return

    def update_text(self, message):
        ''' Add a Troop message to the Queue '''
        while self.ui is None:
            sleep(0.1)
        self.ui.text.write(message)
        return
 
class Node:
    """ Class for basic information on other nodes within the network.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "{}: {}".format(self.hostname, self.port)        
    def __eq__(self, other):
        return self.address == other
    def __ne__(self, other):
        return self.address != other
        





        
