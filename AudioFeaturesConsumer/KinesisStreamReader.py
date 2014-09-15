#!/usr/bin/python
from boto import kinesis

class KinesisStreamReader():
    def __init__(self, region, stream, aws_id, aws_key): 
        self.region = region
        self.stream = stream
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.auth = {'aws_access_key_id':self.aws_id,'aws_secret_access_key' : self.aws_key }

    def InitalizeConnection(self):
        self.conn = kinesis.connect_to_region(self.region, **self.auth)

    def CloseConnection(self):
        self.conn.close()
        
    def GetShardIds(self):
        response = self.conn.describe_stream(self.stream)
        shards = response['StreamDescription']['Shards']
        ids = []
        for shard in shards:
            ids.append(shard['ShardId'])
            
        return ids
    
