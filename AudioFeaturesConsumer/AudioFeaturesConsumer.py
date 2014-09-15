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
import ConfigParser
import sys
import os
import socket
import time

sys.path.append('.')

from DynamoDbPolloer import DynamoDbPolloer
from KinesisStreamReader import KinesisStreamReader

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
#     -Pick a random one and claim ownership of it
#     -"Free" means no one has touched the shard in the last N seconds, where N is the heartbeat period.
#  
# 4) Take ownership of the shard. 
#     -Write to shard record, saying that I own it, and here's the timestamp I took ownership, conditional upon its update time
#     -if write fails because time was already updated,  repeat the above processes until all shards are owned
#     -Otherwise,  if I own it, start processing the shard, 
#
#  5) Processing the shard  
#     -Periodically pull from the shard,
#     -Take the data and put it over to our machine learning module
#     -Take the result of the machine learning module and ship it off... somewhere.

def init(config_file_name):    
    
    #read config file
    config = ConfigParser.ConfigParser()
    f = open(configFileName)
    config.readfp(f)
    f.close()
    
    region = config.get(k_config_section_amazon, k_config_item_region)
    kstream = config.get(k_config_section_amazon, k_config_item_kinesisstream)
    dynamotable = config.get(k_config_section_amazon, k_config_item_dynamodbtable)
    heartbeat_timeout = float(config.get(k_config_section_server,k_config_item_heartbeat_timeout))

    #get secret stuff
    access_key_id = os.getenv(k_env_name_for_amazon_id)
    secret_access_key = os.getenv(k_env_name_for_amazon_secret_key)
    
    #get who I am 
    host_id = socket.gethostname()
    
    #create poller
    dbpoller = DynamoDbPoller(region,dynamotable, access_key_id, secret_access_key, host_id, heartbeat_timeout)
    kreader = KinesisStreamReader(region, kstream,access_key_id, secret_access_key)
    
    
    kreader.init_connection()
    dbpoller.init_connection()
    
    shard_ids = kreader.get_shar_ids()
    
    return (kreader, dbpoller)
    
if __name__ == '__main__':
    config_file_name = sys.argv[1]
    init(config_file_name)
    
    
