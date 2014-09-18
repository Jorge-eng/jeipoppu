#!/usr/bin/python
from boto import kinesis
import logging

class KinesisStreamWriter():
    def __init__(self, region, stream, aws_id, aws_key): 
        self.region = region
        self.stream = stream
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.auth = {'aws_access_key_id':self.aws_id,'aws_secret_access_key' : self.aws_key }
        
    def init_connection(self):
        if self.region != 'local':
            self.conn = kinesis.connect_to_region(self.region, **self.auth)
            
    
    def put_item(self, data, partition_key):
        try:
            self.conn.put_record(self.stream, data, partition_key, b64_encode=True)
        except  Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines)) 
           
   
    #put_record(stream_name, data, partition_key, explicit_hash_key=None, sequence_number_for_ordering=None, exclusive_minimum_sequence_number=None, b64_encode=True)
