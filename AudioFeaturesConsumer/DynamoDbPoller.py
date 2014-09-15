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
k_default_local_port = 7777

class DynamoDbPoller(object):
    def __init__(self, region, table, aws_id, aws_key, host_id, heartbeat_timeout):
        self.region = region
        self.table = table
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.host_id = host_id
        self.heartbeat_timeout = heartbeat_timeout
        
        random.seed(hash(time.time()) + hash(host_id))
     
     #note -- only use this if you're going to create your local table...
     #           these options are probably not right for production
    def create_my_table(self):
        attributes = [{'AttributeName': 'id','AttributeType': 'S'}]
        schema = [{'AttributeName' : 'id','KeyType':'HASH'}]
        throughput = {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}

        self.conn.create_table(attributes,self.table,schema,throughput)
        
        #example -- put an item in 
        #item = {'id':{'S':'myid'},'foo':{'N':'1'}}
        #self.conn.put_item(self.table,item=item)

    def table_exists(self):
        tables =  self.conn.list_tables()['TableNames']
        
        if self.table in tables:
            return True
        else:
            return False

    def init_connection(self):
        print ('Region: %s' % (self.region))
        
        if self.region == 'local':
            print ('using 127.0.0.1')
            self.conn = DynamoDBConnection(host='127.0.0.1',port=k_default_local_port,is_secure=False)
            
            if not self.table_exists():
                print 'Creating Table %s' % self.table 
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
        table = self.GetTable()
        
        try:
            myitem = table.get_item(id=shard)
        
            now = int(time.time())
            host = str(myitem['host'])
            print len(host), len(self.host_id), host, self.host_id
            if host  != self.host_id:
                print ('Another poller named %s replaced me (%s) for shard %s.  Oh the humanity (this was not expected).' %  (host,self.host_id, shard))
                return False
            
            myitem['time'] = now
            if not myitem.save():
                print ('someone took over me before I could save.  What the heck! (this was not expected)')
                return False
            
            return True
        except ItemNotFound:
            print ('can not find shard \"%s\"' % shard)
            return False

        
    #returns id of claimed shard
    def claim_first_available_shard(self, shard_ids):     
        #randomize order of shards
        shards = copy.deepcopy(shard_ids)
        random.shuffle(shards)
        
        myshard = None
        for shard in shards:
            
            myshard = self.claim_shard_if_expired(shard) 
            
            if myshard is not None:
                break;
                
        return myshard
        

    def claim_shard_if_expired(self, shard):
        myshard = None
        
         #get table
        table = self.get_table()
        
        #put, conditional on the time
        now = int(time.time())
        cutoff_time = now - self.heartbeat_timeout
        
        #query for items to see if they exist already
        try:
            myitem = table.get_item(id=shard)
            savedtime = myitem['time']
            host = myitem['host']
            if savedtime < cutoff_time:
                #I claim this for Spain, since no heartbeat seen recently
                myitem['host'] = self.host_id
                myitem['time'] = now
                    
                if myitem.save():
                    myshard = shard
                    
        except ItemNotFound, e:
            #gah! This shard tracking item does not exist yet.  Got put in a new one
            newitem = Item(table,data={'id':shard,'time':now, 'host':self.host_id})
            try:
                newitem.save()
                #if we got here, then victory
                myshard = shard

                print ('Shard %s did not exist yet... creating' % shard)
                    
            except ConditionalCheckFailedException, e:
                #argh, someone saved this item before me!  try another shard.
                foo = 3
                    
        return myshard
