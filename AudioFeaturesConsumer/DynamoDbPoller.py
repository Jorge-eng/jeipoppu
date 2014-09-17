#!/usr/bin/python


import boto
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2 import layer1
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import *
import random
import copy
import time
import random
import logging


k_default_local_port = 7777

k_dynamodb_last_sequence_number = 'last_sequence_number'


class DynamoDbPoller(object):
    def __init__(self, region, table, aws_id, aws_key, host_id, heartbeat_timeout, app_id):
        self.region = region
        self.table = table
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.host_id = host_id
        self.heartbeat_timeout = heartbeat_timeout
        self.myshard = None
        self.app_id = app_id
        
        random.seed(hash(time.time()) + hash(host_id))
     
     #note -- only use this if you're going to create your local table...
     #           these options are probably not right for production
    def create_my_table(self):
        attributes = [{'AttributeName': 'id','AttributeType': 'S'}]
        schema = [{'AttributeName' : 'id','KeyType':'HASH'}]
        throughput = {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}

        self.conn.create_table(attributes,self.table,schema,throughput)
        

    def table_exists(self):
        tables =  self.conn.list_tables()['TableNames']
        
        if self.table in tables:
            return True
        else:
            return False

    def init_connection(self):
        logging.info('Region: %s' % (self.region))
        
        if self.region == 'local':
            logging.info('using 127.0.0.1')
            self.conn = DynamoDBConnection(host='127.0.0.1',port=k_default_local_port,is_secure=False)
            
            if not self.table_exists():
                logging.info( 'Creating Table %s' % self.table )
                self.create_my_table()
                
        else:
            self.conn = boto.dynamodb2.connect_to_region(self.region, 
                        aws_access_key_id=self.aws_id, 
                        aws_secret_access_key=self.aws_key) 
                        
             
    def get_table(self):
        table = Table(self.table) #takes string argument
        table.connection  = self.conn #important if the local connection is used, because by default it starts with us-east-1
        return table
        
    def close_connection(self):
        self.conn.close()
    
    def update_heartbeat(self, shard):
        table = self.get_table()
        
        shard_id = self.myshard + "-" + self.app_id

        try:
            myitem = table.get_item(id=shard_id)
        
            now = int(time.time())
            host = str(myitem['host'])

            if host  != self.host_id:
                logging.warning('Another poller named %s replaced me (%s) for shard %s.  Oh the humanity (this was not expected).' %  (host,self.host_id, shard_id))
                return False
            
            myitem['time'] = now
            if not myitem.save():
                logging.warning ('someone took over me before I could save.  What the heck! (this was not expected)')
                return False
            
            return True
        except ItemNotFound:
            logging.critical ('can not find %s, so I am not updating the heartbeat' % shard_id)
            return False

    def update_shard_sequence_number(self, sequence_number):
        if self.myshard is not None:
            table = self.get_table()
            
            shard_id = self.myshard + "-" + self.app_id

            try:
                myitem = table.get_item(id=shard_id)
                myitem[k_dynamodb_last_sequence_number] = sequence_number
                
                if not myitem.save():
                    logging.warning('Someone saved to shard %s before I (%s) could' % (shard_id, self.host_id) )
                    
    
            except ItemNotFound, e:
            #gah! This shard tracking item does not exist yet.  
                logging.warning('Unable to update %s in DynamoDB with new sequence number' % shard_id)

    #returns id of claimed shard
    def claim_first_available_shard(self, shard_ids):     
        #randomize order of shards
        shards = copy.deepcopy(shard_ids)
        random.shuffle(shards)
        
        myshard = None
        for shard in shards:
            
            myshard, last_sequence_number = self.claim_shard_if_expired(shard) 
            
            if myshard is not None:
                self.myshard = myshard
                break;
                
        return (myshard, last_sequence_number)
        

    def claim_shard_if_expired(self, shard):
        myshard = None
        last_sequence_number = None
        
         #get table
        table = self.get_table()
        
        #put, conditional on the time
        now = int(time.time())
        cutoff_time = now - self.heartbeat_timeout
        
        #query for items to see if they exist already
        shard_id = shard + "-" + self.app_id
        
        try:
            myitem = table.get_item(id=shard_id)
            savedtime = myitem['time']
            host = myitem['host']
            if savedtime < cutoff_time:
                #I claim this for Spain, since no heartbeat seen recently
                myitem['host'] = self.host_id
                myitem['time'] = now
                    
                if myitem.save():
                    myshard = shard
                    last_sequence_number = myitem[k_dynamodb_last_sequence_number]
                    
        except ItemNotFound, e:
            #gah! This shard tracking item does not exist yet.  Got put in a new one
            newitem = Item(table,data={'id':shard_id,'time':now, 'host':self.host_id})
            try:
                newitem.save()
                #if we got here, then victory
                myshard = shard

                logging.warning ('Shard %s did not exist yet... creating' % shard_id)
                    
            except ConditionalCheckFailedException, e:
                #argh, someone saved this item before me!  try another shard.
                foo = 3
                    
        return (myshard, last_sequence_number)
