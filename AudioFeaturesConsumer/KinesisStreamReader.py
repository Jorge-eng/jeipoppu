#!/usr/bin/python
from boto import kinesis
import sys
import traceback
import logging

g_fake_shards = ['fakeshard01', 'fakeshard02', 'fakeshard03']

k_start_pos_latest = 'latest'
k_start_pos_earliest = 'earliest'
k_start_pos_resume = 'resume'


class KinesisStreamReader(object):
    def __init__(self, region, stream, aws_id, aws_key, start_pos): 
        self.region = region
        self.stream = stream
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.auth = {'aws_access_key_id':self.aws_id,'aws_secret_access_key' : self.aws_key }
        self.next_iterator = None
        self.start_pos = start_pos
        self.last_sequence_number = None
        self.myshard = None
        
    def reset_position_to_horizon(self):
        self.next_iterator = None

    def init_connection(self):
        if self.region != 'local':
            self.conn = kinesis.connect_to_region(self.region, **self.auth)

    def close_connection(self):
        self.conn.close()
        
    def set_shard(self, shard):
        self.myshard = shard
        
    def set_last_sequence_number(self, last_sequence_number):
        self.last_sequence_number = last_sequence_number
        
    def get_next_records(self,record_limit = None):
        sequence_number = None
        if self.next_iterator is None:
            if self.start_pos == k_start_pos_latest:
                iterator_type = 'LATEST'
                logging.info('Using latest shard iterator')
            elif self.start_pos == k_start_pos_earliest:
                iterator_type = 'TRIM_HORIZON'
                logging.info('Using earliest shard iterator')
            elif self.start_pos == k_start_pos_resume:
                if self.last_sequence_number is None:
                    iterator_type = 'LATEST'
                    logging.warning('No sequence number to resume from was found... just using latest shard iterator.  Sorry')
                else:
                    sequence_number = self.last_sequence_number
                    iterator_type = 'AFTER_SEQUENCE_NUMBER'
                    logging.info('Using resumed shard iterator %s' % sequence_number)

            else:
                raise NameError('%s was an unrecognized Kinesis start position' % self.start_pos)
                
            response = self.conn.get_shard_iterator(self.stream,self.myshard,iterator_type, sequence_number)
            self.next_iterator = response['ShardIterator']
        
        records = []
        
        try:
            response = self.conn.get_records(self.next_iterator, limit=record_limit, b64_decode=False)
            self.next_iterator = response['NextShardIterator']
            records = response['Records']
            
        except  Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines))  
        
        return records
        
    def get_shard_ids(self):
        if self.region != 'local':
            response = self.conn.describe_stream(self.stream)
            shards = response['StreamDescription']['Shards']
            ids = []
            for shard in shards:
                ids.append(shard['ShardId'])
            
            return ids
            
        else:
            return g_fake_shards
    
