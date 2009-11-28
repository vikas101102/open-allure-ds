'''
This component constantly polls a pygame camera device,
when a message is received on its input it outputs an image.
Created on 29/11/2009

@author: Brian Thorne
'''
import logging
import numpy
from Actor import Source, Actor

import logging
verbose = True
LOG_FILENAME=None
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
WIDTH, HEIGHT = 320, 240


# This requires a recent pygame with a camera module (1.9.1 or greater)
import pygame
import pygame.camera as camera
logging.info("Pygame Version: %s" % pygame.__version__)

class VideoSnapshot(Source):
    '''
    This actor is an image source,
    This component polls a connected webcam, returning the latest
    single image when requested.
    '''

    def __init__(self, input_queue, output_queue, device=0, max_freq=10, size=(WIDTH, HEIGHT),grey=True):
        """
        Constructor for a VideoSnapshot source.

        @param input_queue: A queue that will pass a message when an output
        is desired.

        @param output_queue: The queue that will be passed a tagged image signal.

        @param device: The camera device to connect to - (0 is default)

        @param max_freq: We won't bother polling faster than this max frequency.

        @param size: A tuple containing the width and height to use for the camera
        device.

        @param grey: A boolean indicating if the image should be averaged to one channel
        Example useage:

            >>> msg = {'tag':1,'value':'go'}
            >>> in_queue, out_queue = queue.Queue(), queue.Queue()
            >>> vid_src = VideoSnapshot(in_queue, out_queue)
            >>> in_queue.put(msg)
            >>> in_queue.put(None)  # Tells the component we are finished
            >>> vid_src.start()     # Start the thread, it will process its input queue
            >>> vid_src.join()
            >>> img1 = out_queue.get()
            >>> assert out_queue.get()['value'] == None
        """
        super(VideoSnapshot, self).__init__(self, input_queue=input_queue, output_queue=out)
        self.MAX_FREQUENCY = max_freq
        self.device = device
        self.size = size
        self.grey = grey
        logging.debug("Initializing Video Capture")
        camera.init()

        # gets a list of available cameras.
        self.clist = camera.list_cameras()
        if not self.clist:
            raise IOError("Sorry, no cameras detected.")

        logging.info("Opening device %s, with video size (%s,%s)" % (self.clist[0],self.size[0],self.size[1]))

        self.camera = camera.Camera(self.clist[0], self.size, "RGB")


    def process(self):
        """Carry out the image capture"""
        logging.debug("Running Video capture process")

        # starts the camera
        self.camera.start()

        while True:
            obj = self.input_queue.get(True)     # this is blocking
            if obj is None:
                logging.info("We have finished multiplying the data")
                self.stop = True
                self.output_queue.put(None)
                return
            tag =  obj['tag']

            surface = self.camera.get_image(self.snapshot)

            #Convert the image to a numpy array
            image = surfarray.array3d(surface)
            if self.grey:
                # convert to grayscale numpy array for image processing
                image = numpy.mean(image, 2)

            data = {
                    "tag": tag,
                    "value": image
                    }

            self.output_queue.put(data)
            logging.debug("Video Snapshot process added data at tag: %2." % tag)

