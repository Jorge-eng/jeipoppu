import sys
import base64
import binascii
import traceback
import logging
import time
import copy
import MatrixClientMessageDecoder
 
#functor example
class PassThroughClassifier(object):
    def __init__(self, data):
        self.data = data
        
    def __call__(self, record):
        try:            
            featmat, energysignal, maxenergies = MatrixClientMessageDecoder.time_history_from_matrix_client_message(record)
        
            print len(featmat), len(featmat[0]), len(energysignal), len(maxenergies) 
            
            
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines) )
    
    
            self.classifier = AudioClassifierFactory.get(classifier_id, classifier_data)
            
        return None
        

