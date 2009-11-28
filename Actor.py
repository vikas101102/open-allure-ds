'''
Created on 19/11/2009

@author: Brian Thorne
@project: http://scipy-sim.googlecode.com
'''

import Queue as queue
import threading
import logging


class Actor(threading.Thread):
    '''
    This is a base Actor class for use in a simulation.
    If an input queue was not explicitly passed in, creates one.
    '''
    def __init__(self, input_queue=None, output_queue=None):
        '''
        Asbstort constructor for a generic Actor component.

        @param input_queue: If an input queue is not passed in, one will be created.

        @param output_queue: For consistency all outputs shall be named output_queue
        and can be passed in to this constructor.
        '''

        super(Actor, self).__init__()
        logging.debug("Constructing a new Actor thread")

        # Every actor will have at least an input thread - even if its just a control
        if input_queue is None:
            input_queue = queue.Queue(0)
        self.input_queue = input_queue

        # A source doesn't require an output queue so this could be None
        self.output_queue = output_queue

        self.stop = False
        self.setDaemon(True)


    def run(self):
        '''
        Run this actors objects thread
        '''
        logging.debug("Started running an actor thread")
        while not self.stop:
            #logging.debug("Some actor is processing now")
            self.process()

    def process(self):
        '''
        The process function is called as often as possible by the threading or multitasking library
        No guarantees are made about timing, or that anything will have changed for the input queues
        '''
        raise NotImplementedError()

class Source(Actor):
    '''
    This is just an abstract interface for a signal source.
    Requires an output queue.
    '''

    def __init__(self):
        raise NotImplementedError()

    def process(self):
        raise NotImplementedError()

if __name__ == "__main__":
    my_actor = Actor()

    try:
        my_actor.run()
    except NotImplementedError:
        pass
