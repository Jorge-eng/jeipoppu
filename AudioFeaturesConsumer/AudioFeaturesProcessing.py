#!/usr/bin/python
#
import base64
import matrix_pb2
import sys
import traceback
import time
import binascii
import multiprocessing
import logging

class AudioFeaturesProcessingPool():
    def __init__(self):
        foo = 3
        
        
    def set_records(self, records):
      
        for record in records:
            try:
                message = matrix_pb2.MatrixClientMessage()

                #print record
                b64data = record['Data']
                message.ParseFromString(base64.b64decode(b64data))
                mat = message.matrix_payload
                
                mac = binascii.hexlify(message.mac)

                if mat is not None:
                    duration = mat.time2 - mat.time1
                    logging.info('%s %s %s %s %d %d' % (time.strftime("%X"), mac,  mat.id, mat.tags,mat.time1,duration))
                    
            except Exception, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print ''.join('!! ' + line for line in lines)  # Log it or whatever here
            
