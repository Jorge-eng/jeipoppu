
import sys
import base64
import binascii
import traceback
import logging
import time
import copy
import json
import numpy as np


from proto import matrix_pb2
from proto import classifer_pb2

from MyPca import MyPca
from MyGmm import MyGmmEnsemble

k_min_maxloglik = float(-20.0)

def matrix_message_to_class_message(message):
    mat = message.matrix_payload
            
    mac = binascii.hexlify(message.mac)

    
    class_data = classifer_pb2.audio_class_data()
    classifier_message = classifer_pb2.audio_classifcation_message()

    if mat.idata is not None:
        for i in mat.idata:
            classifier_message.feat_vec.append(float(i))
            

    
    classifier_message.mac = copy.deepcopy(message.mac)
    classifier_message.classifer_key  
    classifier_message.tags  = mat.tags
    classifier_message.source = mat.source
    classifier_message.unix_time = message.unix_time
    classifier_message.time1 = mat.time1
    classifier_message.time2 = mat.time2
    
    return (classifier_message, mac)
   
def probs_to_audio_class_data(probs, maxidx):
    classification = classifer_pb2.audio_class_data()

    for p in probs:
        classification.probability.append(p)

    classification.classes.append(classifer_pb2.audio_class_data.TALKING)
    classification.classes.append(classifer_pb2.audio_class_data.CRYING)
    classification.classes.append(classifer_pb2.audio_class_data.SNORING)
    classification.classes.append(classifer_pb2.audio_class_data.VEHICLE)

    classification.decision = classification.classes[maxidx]
    
    return classification

    
  
#functor for GMM/PCA classification
class GmmAndPcaClassifier():
    def __init__(self, data):
        self.data = data
        
        self.pca = MyPca()
        self.gmm = MyGmmEnsemble()
        
        classifier_dict = json.loads(self.data['serialized_data'])
        
        self.pca.setFromDict(classifier_dict['pca'])
        self.gmm.setFromDict(classifier_dict['gmmsensemble'])
    
    def evaluate(self, mat):
        
        vec = np.array(mat.idata).astype('float')
        vec = vec[1:].reshape(1, len(mat.idata) - 1)

        x = self.pca.transform(vec)
        
        probs = self.gmm.evaluate(x,k_min_maxloglik)
        probs = probs[0] #we are only evaluate one vector at a time
        
        maxidx = np.argmax(probs)
        
        return (probs.tolist(), maxidx)

    
    def __call__(self, record):
        try:
            #deserialize matrix message
            message = matrix_pb2.MatrixClientMessage()
            b64data = record['Data']
            message.ParseFromString(base64.b64decode(b64data))

            classifier_message, mac = matrix_message_to_class_message(message)
            probs, maxidx = self.evaluate(message.matrix_payload)
            classification = probs_to_audio_class_data(probs, maxidx)

            classifier_message.classification.CopyFrom(classification)
            
            bindata = classifier_message.SerializeToString()
            b64data = base64.b64encode(bindata)
            partition = mac
             
            return (b64data, partition)
            
            
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


