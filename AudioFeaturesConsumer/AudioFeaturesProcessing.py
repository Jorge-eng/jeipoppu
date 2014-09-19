#!/usr/bin/python
#
import sys
import time
import logging
import threading
import traceback
from Queue import Queue
from multiprocessing import Pool

sys.path.append('.')
sys.path.append('./machinelearning')

import AudioClassifierFactory


class AudioFeaturesProcessingThread(threading.Thread):
    def __init__(self, classifier_id, classifier_data, numprocs, writer):
        #set up thread
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.writer = writer

        #get classifier function object -- will output classification as a protobuf serialized message
        self.classifier = AudioClassifierFactory.get(classifier_id, classifier_data)
        
        if self.classifier is None:
            logging.critical('could not find the classifier %s in our factory' % classifier)
        else:
            logging.info('Found classifier %s in the factory!' % classifier_id)
            
        #create processing pool 
        logging.info('Starting processing pool with %d processes' % (numprocs))
        self.pool = Pool(numprocs)

    def has_classifier(self):
        if self.classifier is not None:
            return True
        else:
            return False
        
    #exit the thread
    def cancel(self):
        self.queue.put(None)
        
    #put Kinesis records into the queue, where it will get processed    
    def put(self, records):
      
        if records is not None:
            self.queue.put(records)
      
 
    def run(self):
        logging.info('AudioFeatureProcessingThread is running!')
        
        while (True):
            #block until records arrive
            records = self.queue.get()
                        
            if records is None:
                Logging.warning("exiting AudioFeaturesProcessingThread")
                break;
            
            #process records with classifier
            t1 = time.time()
            messages = self.pool.map(self.classifier, records)
            t2 = time.time()
            
            #THIS COULD BE A BOTTLENECK, PUTTING THEM IN ONE AT A TIME
            t3 = time.time()

            if messages is not None:
                for item in messages:
                    if item is not None:
                        message = item[0]
                        partition = item[1]
                        
                        self.writer.put_item(message, partition)
                    
            t4 = time.time()
            
            logging.info('AudioFeaturesProcessingThread: %f seconds to process %d items, %f seconds to send' % (t2-t1, len(records), t4-t3) )

            self.queue.task_done()
