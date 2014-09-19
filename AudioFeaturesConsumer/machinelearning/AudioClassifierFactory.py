import sys

from PassThroughClassifier import PassThroughClassifier
from AudioClassifierSimpleGmmAndPca import GmmAndPcaClassifier

CLASSIFIER_PASS_THROUGH = "CLASSIFIER_PASS_THROUGH"
CLASSIFIER_GMM_PCA = "CLASSIFIER_GMM_PCA"

def get(classifier_id, classifier_data):
    factory_dict = {
                    CLASSIFIER_PASS_THROUGH : PassThroughClassifier, 
                    CLASSIFIER_GMM_PCA : GmmAndPcaClassifier
                    }
    
    if not factory_dict.has_key(classifier_id):
        return None
        
    return factory_dict[classifier_id](classifier_data)
    
