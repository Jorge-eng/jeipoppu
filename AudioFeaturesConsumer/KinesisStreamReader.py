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

    def init_connection(self):
        if self.region != 'local':
            self.conn = kinesis.connect_to_region(self.region, **self.auth)

    def close_connection(self):
        self.conn.close()
        
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
    
