#!/usr/bin/python
import sys
import traceback
import logging
import time
import copy
import MatrixClientMessageDecoder
from EnergySummary import *
from MyLinearSvm import *
import DataKeys

class LinearSvmAndEnergySummarizer(object):
    def __init__(self, data):
        classifier_data = data[DataKeys.k_classifier_data]
        self.svm = MyLinearSvm(classifier_data)
        
        
    def __call__(self, record):
        try:       
            #extract all data from record
            featmat, energysignal, maxenergies, unix_time, partitionkey = MatrixClientMessageDecoder.time_history_from_matrix_client_message(record)
            
            #get energy summary
            max_energy_in_db, disturbance_count = get_energy_summary(energysignal, maxenergies)
            
            #run classifier on data
            decisions = self.svm.evaluate(featmat)
            
            return (serializedb64, partitionkey)
            
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines) )
    
    
            self.classifier = AudioClassifierFactory.get(classifier_id, classifier_data)
            
            return None
        

