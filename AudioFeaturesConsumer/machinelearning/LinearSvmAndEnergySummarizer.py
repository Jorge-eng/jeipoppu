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
import base64

from proto import audio_classification_pb2

class LinearSvmAndEnergySummarizer(object):
    def __init__(self, data):
        #classifier_data = data[DataKeys.k_classifier_data]
        #self.svm = MyLinearSvm(classifier_data)

        #maps clasifier output to enums contained in 
        #output protobuf
        #self.class_map = data[DataKeys.k_class_map]
        foo = 3
        
    def __call__(self, record):
        try:       
            #extract all data from record
            featmat, energysignal, maxenergies, unix_time, device_id = MatrixClientMessageDecoder.time_history_from_matrix_client_message(record)
            
            #get energy summary
            max_energy_in_db, disturbance_count = get_energy_summary(energysignal, maxenergies)
            
            #run classifier on data
            #decisions = self.svm.evaluate(featmat)
            
            output = audio_classification_pb2.audio_classifcation_message()
            
            output.device_id = device_id
            output.unix_time = unix_time
            output.energies.num_disturbances = disturbance_count
            print max_energy_in_db
            output.energies.max_decibel_over_background = max_energy_in_db
            
            #nothing happening for now
            output.classes.probability.append(1.0)
            output.classes.classes.append(output.classes.NULL)
            
            serializedb64 = base64.b64encode(output.SerializeToString())

            #return serialized data, and partition key
            return (serializedb64, device_id)
            
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines) )
    
    
            self.classifier = AudioClassifierFactory.get(classifier_id, classifier_data)
            
            return None
        

