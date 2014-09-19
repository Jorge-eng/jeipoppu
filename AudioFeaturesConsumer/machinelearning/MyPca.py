#!/usr/bin/python

import numpy as np
import numpy.linalg


class MyPca(object):
    def fit(self, x, ndimsout):
        #print np.cov(feats.transpose, axis).shape
        mean =  np.mean(x, axis=0).reshape(1, x.shape[1])
        meanmat = np.tile(mean, (x.shape[0], 1))
        print meanmat.shape
        nomeanfeats = x - meanmat
        P = np.cov(nomeanfeats.transpose())
        d = np.sqrt(np.diagonal(P))

        for j in range(nomeanfeats.shape[1]):
            nomeanfeats[:, j] = nomeanfeats[:, j] / d[j]
    
        P2 = np.cov(nomeanfeats.transpose())

        w, v = np.linalg.eig(P2)

        transform = v[:, 0:ndimsout]
        
        self.covdiags = d
        self.explainedvariance = d / np.sum(d)
        self.mean = mean
        self.rotation = transform
        #self.reducedfeats_ = f2
        
     #takes a bunch of row vectors   
    def transform(self, x):
        #subtrac tmean
        meanmat = np.tile(self.mean, (x.shape[0], 1))
        nomeanfeats = x - meanmat
        
        #normalize by variance
        for j in range(nomeanfeats.shape[1]):
            nomeanfeats[:, j] = nomeanfeats[:, j] / self.covdiags[j]
        
        #"rotate" and reduce dimensions
        retmat =  np.matrix(nomeanfeats) * np.matrix(self.rotation)
        return np.array(retmat)
        
    def to_dict(self):
        me = {}
        me['covdiags'] = self.covdiags.tolist()
        me['transform'] = self.rotation.tolist()
        me['mean'] = self.mean.tolist()
        return me
        
    def set_from_dict(self, me):
        self.covdiags = np.array(me['covdiags'])
        self.rotation = np.array(me['transform'])
        self.mean = np.array(me['mean'])




