from proto import matrix_pb2
from proto import classifer_pb2
import binascii
import base64
from sets import set
import logging

k_occurence_indices_buf_id = "occurenceIndices"
k_occurence_durations_buf_id = "occurenceDurations"
k_occurence_deltatimes_buf_id = "occurenceDeltaTimes"
k_feat_vec_buf_id = "featVecs"
k_feat_index_buf_id = "featIndices"
k_occurence_info_buf_id = "occurenceInfo"

k_occurence_idx_idx = 0
k_occurence_num_idx = 1


all_necessary_keys = Set([k_occurence_indices_buf_id, k_occurence_durations_buf_id, k_occurence_deltatimes_buf_id, k_feat_vec_buf_id, k_feat_index_buf_id, k_occurence_info_buf_id])

def pbmat_idata_to_mat(pbmat):
    mat = []
    
    k = 0
    for j in range(pbmat.rows):
        row = []
        for i in range(pbmat.cols):
            row.append(pbmat.idata[k])
            k = k + 1
        mat.append(row)
        
    return mat
    
   
#
#
#  We get 6 pieces of information to assemble 2 things
#  1) dict of feature vectors, where the key is the index
#  2) time ordered list of "occurences", which tell us 
#     a) which feature vector it belongs to
#     b) its duration, and spacing with previous segment
#  
#
class ClientParser(object):
    def ParseFromBase64String(self, base64data):
        try:
            bindata = base64.b64decode(base64data)
        
            message = matrix_pb2.MatrixClientMessage()
            
            message.ParseFromString(bindata)
            
            #extract everything useful
            
            self.mac = binascii.hexlify(message.mac)
            self.tags = message.tags
            self.source = message.source
            self.unix_time = message.unix_time
            self.time1 = message.time1
            self.time2 = message.time2
            
            matdict = {}
            
            for matrix in message.matrix_list:
                matdict[matrix.id] = pbmat_idata_to_mat(matrix)
            
           
            #check and make sure that all required keys were present
            all_my_keys = Set(matdict.keys())
            
            setdiff = all_necessary_keys.difference(all_my_keys)
            
            if setdiff:
                logging.warning('%s at unix_time %d did not have all requried keys ' % (self.mac, message.unix_time) )
                return False
           
            #now that I have the matrices, time to assemble them into a list of time ordered features
            infovec = matdict[k_occurence_info_buf_id]
            startidx = infovec[k_occurence_idx_idx]
            numoccurences = infovec[k_occurence_num_idx]
            
            #go make my items in one array
            indices = matdict[k_occurence_indices_buf_id]
            durations = matdict[k_occurence_durations_buf_id]
            dts = matdict[k_occurence_deltatimes_buf_id]
            
            if not (len(indices) == len(durations) and len(durations) == len(dts)):
                logging.warning('%s at unix_time %d has unequal length occurence vectors ' % (self.mac, message.unix_time) )
                return False
        
            occurences = []
            for i in range(len(indices)):
                occurences.append((indices[i], durations[i], dts[i]) )
                
            #now re-arrange in order, because the orignal list was a cirulcar buffer
            endidx = (startidx + numoccurences - 1) % len(indices) 

            orderedoccurences = []
            orderedoccurences.append(occurences[startidx:(endidx+1)])
            orderedoccurences.append(occurences[0:startidx])
            
            #now compute times
            #TODO  -- Go from time2 backwards with durations
                
            #create dict for feature vectors where the key is the index number
            vecs = matdict[k_feat_vec_buf_id]
            featindices = matdict[k_feat_index_buf_id]
            
            if len(featindices) != len(vecs):
                logging.warning('%s at unix_time %d has unequal length feature vectors ' % (self.mac, message.unix_time) )

            featdict = {}
            for i in range(len(featindices)):
                featdict[featindices[i]] = vec[i]
            
            #assemble feature vectors
            for index, duration, dt in orderedoccurences:
                
                #ignore features that were dropped from the list
                #it is a result from old feature vectors being dropped
                #in favor of new ones
                if featdict.has_key(index):
                    v = featdict[index]
            
            
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines) )
            
            
        return True

    
