#!/usr/bin/python
from boto import kinesis

g_fake_shards = ['fakeshard01', 'fakeshard02', 'fakeshard03']

class KinesisStreamReader(object):
    def __init__(self, region, stream, aws_id, aws_key): 
        self.region = region
        self.stream = stream
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.auth = {'aws_access_key_id':self.aws_id,'aws_secret_access_key' : self.aws_key }
        self.next_iterator = None
        
    def reset_position_to_horizon(self):
        self.next_iterator = None

    def init_connection(self):
        if self.region != 'local':
            self.conn = kinesis.connect_to_region(self.region, **self.auth)

    def close_connection(self):
        self.conn.close()
        
    def set_shard(self, shard):
        self.myshard = shard
        
    def get_next_records(self, record_limit = 25):
        if self.next_iterator is None:
            response = self.conn.get_shard_iterator(self.stream,self.myshard,'TRIM_HORIZON')
            self.next_iterator = response['ShardIterator']
        
        records = []
        
        try:
            response = self.conn.get_records(self.next_iterator, limit=record_limit)
            self.next_iterator = response['NextShardIterator']
            records = response['Records']
            
        except  Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print ''.join('!! ' + line for line in lines)  # Log it or whatever here
        
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
    
