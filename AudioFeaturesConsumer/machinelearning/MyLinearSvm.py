#!/usr/bin/python
import numpy as np
import json

class MyLinearSvm(object):
    def deserialize_from_json(self,jdata):
        mydict = json.loads(jdata);
         #weights should be [c x nfeat]
        self.weights = np.matrix(mydict['weights'])
        
        #bias should be [c x 1]
        self.bias = np.matrix(mydict['bias'])
        
        
        self.biastile = np.tile(self.bias, self.weighs.shape[1])

    def evaluate(self, feats_as_rowvecs):
        #weights [c x nfeat]
        #feats  [m x nfeat]
        #feat * weight^T  = [m x c]
        evals = np.matrix(feats_as_rowvecs) * self.weights.transpose() + self.biastile
        
        return evals
        
