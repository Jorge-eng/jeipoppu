import sys
import base64
import binascii
import traceback
import logging
import time

sys.path.append('../proto')

import matrix_pb2
import classifer_pb2

CLASSIFIER_PASS_THROUGH = "CLASSIFIER_PASS_THROUGH"

def get(classifier_id, classifier_data):
    factory_dict = {CLASSIFIER_PASS_THROUGH : PassThroughClassifier}
    
    if not factory_dict.has_key(classifier_id):
        return None
        
    return factory_dict[classifier_id](classifier_data)
    

#functor example
class PassThroughClassifier():
    def __init__(self, data):
        self.data = data
        
    def __call__(self, record):
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
    
    
            self.classifier = AudioClassifierFactory.get(classifier_id, classifier_data)
            
        return None
