#!/usr/bin/python
import sys
import base64
import binascii
import traceback
import logging
import time
import copy
import json
import numpy as np

k_energy_matrix_id = 'energy_chunk'
k_mfcc_matrix_id = 'feature_chunk'

from proto import matrix_pb2

def extract_matrix(mat):
    outlist = []
    #print('matrix rows=%d,cols=%d' % (mat.rows, mat.cols))
    k = 0
    for j in range(mat.rows):
        templist = []

        for i in range(mat.cols):
            templist.append(float(mat.idata[k]))
            k = k + 1
            
        outlist.append(templist)
        
    return outlist
            

def time_history_from_matrix_client_message(record):
    featmat = []
    energysignal = []
    maxenergies = []
    times = []
    
    try:
        #deserialize matrix message
        message = matrix_pb2.MatrixClientMessage()
        b64data = record['Data']
        bindata = base64.b64decode(b64data)
        message.ParseFromString(bindata)
        
        mac_hex = binascii.hexlify(message.mac)
        unix_time = message.unix_time
        device_id = mac_hex
        
        #process repeated matrix entries
        N = len(message.matrix_list)
 
        for i in range(N):
            mat = message.matrix_list[i];
            
            t1 = mat.time1
            t2 = mat.time2
            
            #get a list of lists, (i.e. a matrix)
            templist = extract_matrix(mat) 
            
            if mat.id == k_energy_matrix_id:
                templist = templist[0];
                maxenergy = templist[-1]
                energies = templist[:-1]
                
                energysignal.extend(energies)
                maxenergies.append(maxenergy)
                
            elif mat.id == k_mfcc_matrix_id:
                for vec in templist:
                    featmat.append(vec)
                
            else:
                logging.warning("found audio feature chunks that do not have a valid ID: %s", mat.id)
                
            
    except Exception, e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logging.warning(''.join('!! ' + line for line in lines) )
        


    return (featmat, energysignal, maxenergies, unix_time, device_id)
