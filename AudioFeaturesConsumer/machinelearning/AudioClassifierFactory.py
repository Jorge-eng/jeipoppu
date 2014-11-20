import sys

from PassThroughClassifier import PassThroughClassifier
from LinearSvmAndEnergySummarizer import LinearSvmAndEnergySummarizer

CLASSIFIER_PASS_THROUGH = "CLASSIFIER_PASS_THROUGH"
CLASSIFIER_LINEAR_SVM_AND_HMM = "CLASSIFIER_LINEAR_SVM_AND_HMM"

def get(classifier_id, classifier_data):
    factory_dict = {
                    CLASSIFIER_PASS_THROUGH : PassThroughClassifier,
                    CLASSIFIER_LINEAR_SVM_AND_HMM : LinearSvmAndEnergySummarizer
                    }
    
    if not factory_dict.has_key(classifier_id):
        return None
        
    return factory_dict[classifier_id](classifier_data)
    
