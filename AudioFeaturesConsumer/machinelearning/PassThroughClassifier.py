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
        
        
#message audio_class_data {
#  enum audio_class {
#    UNKNOWN = 0;
#    NULL = 1;
#    TALKING = 2;
#    CRYING = 3;
#    SNORING = 4;
#    VEHICLE = 5;
#  }
#
#  repeated float probability       = 1; //probability vector
#  repeated audio_class classes     = 2; //which element in prob vector is what
#  optional audio_class decision    = 3; //the class on which we decided
#}
#
#message audio_classifcation_message {
#
#  repeated float feat_vec                        = 1;//original raw features
#  optional audio_class_data classification       = 2;//output of classifer
#  optional int64 time1                           = 3;//segment start time in nanoseconds, referenced from.... boot?
#  optional int64 time2                           = 4;//segment end time in nanoseconds
#  optional int32 unix_time                       = 5;//form the client -- wall time UTC, seconds since 1970
#  optional string classifer_key                  = 6;//which S3 key we used for this classifer
#  optional string tags                           = 7;//from the client (i.e. Morpheus, or whatever), usually a comma separated list of things like "steady"
#  optional string source                         = 8;//from the client, which item this was from
#  optional bytes mac                             = 9;//mac address of client (basically related to user ID)
#  optional string userid                         = 10; // user id, from our database, redundant with mac address, but may help us a lot with aggregation
#
#}


