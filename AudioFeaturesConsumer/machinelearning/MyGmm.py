#!/usr/bin/python
import numpy as np
import numpy.linalg
import scipy.linalg


class MyGmm(object):
    def init(self):
        self.L = []
        self.LTInv = []
        self.denom_ = []
        
        logk2pi_ = -0.5 * np.log(np.pi * 2)*self.dim

        for i in range(self.nmodels):
            mat = np.matrix(self.covars[i])
            mychol = scipy.linalg.cholesky(mat)
            mycholInverseTranspose = np.linalg.inv(mychol).transpose()

            #compute sqrt(det(covariance))
            k = 1;
            for j in range(self.dim):
                k = k * mychol[j, j]   
          
            self.denom_.append(-np.log(k) + logk2pi_)
            
            self.L.append(mychol)
            self.LTInv.append(mycholInverseTranspose)
        
        

        
    def set_from_sklearn_gmm(self, g):
        self.covars = g.covars
        self.means = g.means
        self.weights = g.weights
        self.dim = self.covars.shape[1]
        
        if len(self.covars[0].shape) == 1:     
            cs = []
       
            for j in range(len(self.covars)):
                cs.append(np.diag(self.covars[j]))

            self.covars = [] 
            for c in cs:
                self.covars.append(c)
			
            self.covars = np.array(self.covars)
            
            self.nmodels = len(self.covars)

        else:
            self.nmodels = self.covars.shape[0]
        self.init()
        
    def to_dict(self):
        me = {}
        me['covars'] = self.covars.tolist()
        me['means'] = self.means.tolist()
        me['weights'] = self.weights.tolist()
        me['dim'] = self.dim
        me['nmodels'] = self.nmodels
        return me
        
    def set_from_dict(self, me):
        self.covars = np.array(me['covars'])
        self.means = np.array(me['means'])
        self.weights = np.array(me['weights'])
        self.dim = me['dim']
        self.nmodels = me['nmodels']
        self.init()


    #excepts x as a bunch of rows
    def evaluate(self, x):
        logliksum = np.array([])
        first = True
        for imodel in range(self.nmodels):
            loglik = self.evalgaussian(self.L[imodel], self.LTInv[imodel], self.weights[imodel], self.means[imodel], self.denom_[imodel], x)

            if first:
                logliksum = loglik
            else:
                logliksum = logliksum + loglik
         
        return logliksum.reshape( (len(logliksum), 1))
        
    def evalgaussian(self, L, LTInv, w, mean, loglikdenom, x):
        # lik  == 1/sqrt( (2*pi)^k * det(P))  * exp[ -0.5 (x-mu)^T  * P^-1 * (x-mu) ]
        # L = cholesky decomposition of P, P^-1 = (L'L)^-1 = L^-1 * L'^-1
        # y = (L^T)^-1 * (x - mu)  
        # log(lik) = -1/2 [k*log(2*pi)] - 0.5*log(L(1,1)) - 0.5*log(L(2,2)) ... -0.5 *log(L(N,N))  - 0.5 y^T * y
        #print np.tile(mean, (x.shape[0], 1))
        xnomean = x - np.tile(mean, (x.shape[0], 1))

        xt = xnomean.transpose()
        y = np.matrix(LTInv) * xt
                
        y = np.array(y)
        
        y = y * y;
        
        y = np.sum(y, axis=0)
        y = y * -0.5
        loglik = y + loglikdenom
                
        return loglik


class MyGmmEnsemble():
    def __init__(self):
        self.gmm = []
        
    def add_gmm(self, g):
        self.gmm .append(g)
        
    def to_dict(self):
        me = []
        for g in self.gmm:
            me.append(g.to_dict())
        
        return me
        
    def set_from_dict(self, me):
        
        for item in me:
            g = MyGmm()
            g.set_from_dict(item)
            self.add_gmm(g)
            
    def evaluate(self, x, minmaxloglik = -20):
        max = 0.0
        
        #evaluate, possibly in batch
        first = True
        for g in self.gmm:
            if first:
                y = g.evaluate(x)
                first = False
            else:
                y2 = g.evaluate(x)
                y = np.concatenate((y,y2 ), axis=1)

        #compute maximum log liklihood for each evaluation
        maxloglik = np.amax(y, axis=1).reshape((y.shape[0], 1))

        #subtract to keep in sane range after exp
        y= y - np.tile(maxloglik, (1, y.shape[1]))
        
        z = np.exp(y)
        
        #normalize probabilties to sum to 1.0
        probsum = np.sum(z, axis=1).reshape((y.shape[0], 1))
        probs = z / np.tile(probsum, (1, y.shape[1]))
        
        probs[np.where(maxloglik < minmaxloglik), :] = 0
        
        return probs
        

