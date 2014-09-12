#!/usr/bin/python
#
#  Note, be sure to have your AWS credentials in ~/.boto
#  
#  [Credentials]
# aws_access_key_id = BLARGABLARGABLARG
# aws_secret_access_key = xyxzpq4wtfa1sflas4hdf5lsdhfsdl
#
#

# You must have boto installed
import boto
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2 import *
from boto import kinesis
import ConfigParser
import sys
import os
import socket
import time

sys.path.append('.')


k_config_section_amazon = 'amazon'
k_config_section_server = 'server'

k_config_item_region = 'region'
k_config_item_kinesisstream = 'kinesis-stream'
k_config_item_dynamodbtable = 'dynamodb-table'
k_config_item_heartbeat_timeout = 'heartbeat-timeout'

k_env_name_for_amazon_id = 'AWS_ACCESS_KEY_ID'
k_env_name_for_amazon_secret_key = 'AWS_SECRET_KEY'

k_key_shard = 'shard'
k_key_time = 'time'
k_key_owner = 'owner'

# 1) Get your info, like host name, that uniquely identifies this instance
#
# 2) Go to Kinesis on the cloud and see how many shards there are, and what their id is.
# 
# 3) Go check the AudioFeaturesConsumer table on our dynamo DB 
#     -Query to see if there are any free shards to consume
#     -"Free" means no one has touched the shard in the last N seconds, where N is the heartbeat period.
#  
# 4) Take ownership of the shard. 
#     -Write to shard record, saying that I own it, and here's the timestamp I took ownership
#     -Read from record after a few seconds, to verify that I did indeed take ownership (someone else may have beaten me to it)
#     - If I own it, start processing the shard, otherwise repeat the above process until all shards are owned
#
#  5) Processing the shard  
#     -Periodically pull from the shard,
#     -Take the data and put it over to our machine learning module
#     -Take the result of the machine learning module and ship it off... somewhere.


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
    
class DynamoDbPoller():
    def __init__(self, region, table, aws_id, aws_key, host_id, heartbeat_timeout):
        self.region = region
        self.table = table
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.host_id = host_id
        self.heartbeat_timeout = heartbeat_timeout
        
        
    def InitalizeConnection(self):
        self.conn = boto.dynamodb2.connect_to_region(self.region, 
                        aws_access_key_id=self.aws_id, 
                        aws_secret_access_key=self.aws_key) 
                        
                        
    def CloseConnection(self):
        self.conn.close()
        
    
    def FindUnownedShards(self):
        now = time.time()
        
        db = Table(self.table)
        results = db.scan()

        free_shards = []
        for r in results:
            if r.has_key(k_key_shard) and r.has_key(k_key_time) and r.has_key(k_key_owner):
                rtime = r[k_key_time]
                
                if time - rtime > self.heartbeat_timeout:
                    free_shards.append(r[k_key_shard])
                    
        return free_shards   
                
     
    def Claim
        
def Init(configFileName):    
    
    #read config file
    config = ConfigParser.ConfigParser()
    f = open(configFileName)
    config.readfp(f)
    f.close()
    
    region = config.get(k_config_section_amazon, k_config_item_region)
    kstream = config.get(k_config_section_amazon, k_config_item_kinesisstream)
    dynamotable = config.get(k_config_section_amazon, k_config_item_dynamodbtable)
    heartbeat_timeout = config.get(k_config_section_server,k_config_item_heartbeat_timeout)
    
    #get secret stuff
    access_key_id = os.getenv(k_env_name_for_amazon_id)
    secret_access_key = os.getenv(k_env_name_for_amazon_secret_key)
    
    #get who I am 
    host_id = socket.gethostname()
    
    #create poller
    dbpoller = DynamoDbPoller(region,dynamotable, access_key_id, secret_access_key, host_id, heartbeat_timeout)
    kreader = KinesisStreamReader(region, kstream,access_key_id, secret_access_key)
    
    
    kreader.InitalizeConnection()
    dbpoller.InitalizeConnection()
    
    return (kreader, dbpoller)
    
if __name__ == '__main__':
    configFileName = sys.argv[1]
    Init(configFileName)
    
    
