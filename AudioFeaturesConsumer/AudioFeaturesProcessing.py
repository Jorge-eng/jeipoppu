#!/usr/bin/python
#
import base64
import matrix_pb2
import sys
import traceback
import time
import binascii
from multiprocessing import Pool
import logging
from machinelearning import AudioClassifierFactory


def process_pool_func(record,classifier):
    try:
        message = matrix_pb2.MatrixClientMessage()
    
        #print record
        b64data = record['Data']
        message.ParseFromString(base64.b64decode(b64data))
        mat = message.matrix_payload
        
        mac = binascii.hexlify(message.mac)
    
        if mat is not None:
            #pass of
            duration = mat.time2 - mat.time1
            logging.info('%s %s %s %s %d %d' % (time.strftime("%X"), mac,  mat.id, mat.tags,mat.time1,duration))
        
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logging.warning(''.join('!! ' + line for line in lines) )


class AudioFeaturesProcessingPool():
    def __init__(self, classifier_id, classifier_data, numpools):
        self.classifier = AudioClassifierFactory.get(classifier_id)
        
        if self.classifier.get(classifier) is None:
            logging.critical('could not find the classifier %s in our factory' % classifier)
            
        self.pool = Pool(numpools)
        
    def set_records(self, records):
      
        #package classifier function object along with data.
        processing_list = []
        for record in records:
            processing_list.append((record,self.classifier))
      
        #evaluate in thread pool
        self.pool.map(process_pool_func, processing_list)
      
 
            
