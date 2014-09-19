
#!/usr/bin/python
import boto.s3
from boto.s3.bucket import Bucket
from boto.s3.bucket import Key
import logging
import sys
import traceback

class S3BucketReader(object):
    def __init__(self, region, bucket_id,  aws_id, aws_key):
        self.region = region
        self.aws_id = aws_id
        self.aws_key = aws_key
        self.bucket_id = bucket_id
        self.auth = {'aws_access_key_id':self.aws_id,'aws_secret_access_key' : self.aws_key }

        
    def init_connection(self):
        self.conn = boto.s3.connect_to_region(self.region, **self.auth)
        
        if self.conn is None:
            logging.critical('Unable to establish connection to S3!')
            raise Exception('Unable to establish connection to S3')

        self.bucket = self.bucket_id
        
        return self
    
    def get_all_keys(self):
        bucket = Bucket(self.conn, self.bucket_id)
        
        return bucket.get_all_keys()
        
    def get_value(self, key):
        bucket = Bucket(self.conn, self.bucket_id)
        item = Key(bucket)
        item.key = key
        try:
            value = item.get_contents_as_string()
        except Exception, e:
            value = None
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.warning(''.join('!! ' + line for line in lines))  
            
        return value

    #gets key specified, and uses that bucket as a 
    def get_linked_value(self, key):
        key2 = self.get_value(key)
        value = None
        if key2 is not None:
            value = self.get_value(key2)
            
        return value
            
        
        
