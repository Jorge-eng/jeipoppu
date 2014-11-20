#!/usr/bin/python
import numpy as np

class MyHmm(object):
    def __init__(self, hmmdata):
        self.stm = np.array(hmmdata['stm'])
        self.cond_probs = np.array(hmmdata['cond_probs'])
