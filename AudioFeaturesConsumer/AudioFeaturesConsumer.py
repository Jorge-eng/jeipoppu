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
import threading
import signal
import sys
import time
import datetime
import logging 

sys.path.append('../')

from DynamoDbPoller import DynamoDbPoller
from KinesisStreamReader import KinesisStreamReader
from KinesisStreamWriter import KinesisStreamWriter
from S3BucketReader import S3BucketReader
import AudioFeaturesProcessing

k_number_of_records_consumed_before_updating_dbpoller = 100
k_record_limit_per_pull = 100
k_idle_wait_period_to_poll_stream = 2

k_config_section_amazon = 'amazon'
k_config_section_server = 'server'
k_config_section_client = 'client'

k_config_item_appid = 'app-id'
k_config_item_region = 'region'
k_config_item_kinesisstartpos = 'kinesis-start-position'
k_config_item_readkinesisstream = 'kinesis-read-stream'
k_config_item_writekinesisstream = 'kinesis-write-stream'
k_config_item_dynamodbtable = 'dynamodb-table'
k_config_item_heartbeat_timeout = 'heartbeat-timeout'
k_config_item_logfile = 'log-file'
k_config_item_loglevel = 'log-level'
k_config_item_printtostdout = 'print-to-stdout'
k_config_item_classifierid = 'classifier-id'
k_config_item_s3classifierkey = 's3-classifier-key'
k_config_item_s3classifierbucket = 's3-classifier-bucket'
k_config_item_numprocesses = 'num-processes'

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

g_timer = None


    
class HeartbeatTimer(threading.Thread):
    def __init__(self, poller, shard, heartbeat_period):
        threading.Thread.__init__(self)
        self.poller = poller
        self.shard = shard
        self.heartbeat_period = heartbeat_period
        self.kill = False

    def heartbeat(self):
        if (self.poller.update_heartbeat(self.shard)):
            logging.info('heartbeat')
            foo = 3
        else:
            logging.warning('FAILED HEARTBEAT')
        
    def cancel(self):
        self.kill = True
        
    def run(self):
        while (not self.kill):
            time.sleep(self.heartbeat_period)
            self.heartbeat()
            
        logging.info('Succesful thread shutdown')
            
def init(config_file_name):
    global g_timer
    
    
    #read config file
    config = ConfigParser.ConfigParser()
    f = open(config_file_name)
    config.readfp(f)
    f.close()
    
    region = config.get(k_config_section_amazon, k_config_item_region)
    kinesis_startpos = config.get(k_config_section_amazon, k_config_item_kinesisstartpos)

    stream_to_read = config.get(k_config_section_amazon, k_config_item_readkinesisstream)
    stream_to_write = config.get(k_config_section_amazon, k_config_item_writekinesisstream)
    dynamotable = config.get(k_config_section_amazon, k_config_item_dynamodbtable)

    heartbeat_timeout = float(config.get(k_config_section_server,k_config_item_heartbeat_timeout))
    logfilename = config.get(k_config_section_client, k_config_item_logfile)
    loglevel = config.get(k_config_section_client, k_config_item_loglevel)
    printout = config.get(k_config_section_client, k_config_item_printtostdout)
    
    classifier_id = config.get(k_config_section_client, k_config_item_classifierid)
    classifier_s3_key = config.get(k_config_section_amazon, k_config_item_s3classifierkey)
    classifier_s3_bucket = config.get(k_config_section_amazon, k_config_item_s3classifierbucket)

    app_id = config.get(k_config_section_client, k_config_item_appid)
    numproc = config.get(k_config_section_client, k_config_item_numprocesses)
    numproc = int(numproc)
    
    #get secret stuff
    access_key_id = os.getenv(k_env_name_for_amazon_id)
    secret_access_key = os.getenv(k_env_name_for_amazon_secret_key)
    
    #get who I am 
    host_id = socket.gethostname()
    
    #create poller
    dbpoller = DynamoDbPoller(region,dynamotable, access_key_id, secret_access_key, host_id, heartbeat_timeout, app_id)
    
    #set up kinesis reader so we can find out which shards exist
    kreader = KinesisStreamReader(region, stream_to_read,access_key_id, secret_access_key, kinesis_startpos)
    kreader.init_connection()

    #set up logging
    logging.basicConfig(filename=logfilename,level=loglevel, 
                        format='%(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
                        
         
    #if we have been configured to also log to std out, do so
    if printout:
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(loglevel)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    
    #initialize dynamoDB connection
    dbpoller.init_connection()
    
    #figure out which shard I am using
    shard_ids = kreader.get_shard_ids()
    myshard, last_sequence_number = dbpoller.claim_first_available_shard(shard_ids)

    success = False
    processor = None

    #if successful in getting a shard, set up everything else
    if myshard is not None:
        logging.info ('Claimed %s' % (myshard + '-' + app_id))

        #our writer to another kinesis stream
        kwriter = KinesisStreamWriter(region, stream_to_write, access_key_id, secret_access_key)
        kwriter.init_connection()
        
        #set up heartbeat
        interval = heartbeat_timeout/2
        logging.info ('starting heartbeat timer with interval of %d seconds' % (interval))
        
        g_timer = HeartbeatTimer(dbpoller, myshard, interval)
        g_timer.setDaemon(True)
        g_timer.start()

        kreader.set_shard(myshard)
        kreader.set_last_sequence_number(last_sequence_number)
        
        #if we can get data from amazon for our classifier....
        s3reader = S3BucketReader(region, classifier_s3_bucket, access_key_id, secret_access_key).init_connection()
        

        if s3reader.conn is not None:
            classifier_data = {}

            my_classifier_key = s3reader.get_value(classifier_s3_key)
            
            classifier_data['serialized_data'] = s3reader.get_linked_value(classifier_s3_key)
            classifier_data['key'] = my_classifier_key
            
            #set up processor
            processor = AudioFeaturesProcessing.AudioFeaturesProcessingThread(classifier_id, classifier_data, numproc, kwriter)
            
            if processor.has_classifier():
                processor.setDaemon(True)
                processor.start()
                success = True
           
    if (success):
        logging.info('Reading from stream %s' % (stream_to_read))
        logging.info('Writing to stream %s' % (stream_to_write))

        
        
    return (success, kreader,processor, dbpoller)
    
def deinit():
    global g_timer

    if g_timer is not None:
        g_timer.cancel()
        
        
        
def signal_handler(signal, frame):
        logging.info ('caught the ctrl-c')
        deinit()
        sys.exit(0)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal_handler)


    config_file_name = sys.argv[1]
    success, kreader, processor, dbpoller = init(config_file_name)
    
    
    if (success is True):
        
        records_consumed = 0

        ###### MAIN PROGRAM LOOP ######
        while(True):
            #get the records from kinesis
            records = kreader.get_next_records(record_limit=k_record_limit_per_pull)
                        
            #did we get any?
            if len(records) > 0:
                
                #process!
                processor.put(records)
                
                records_consumed += len(records)
                
                #if we have exceeded the number of records required to update our sequence number, we do so
                if (records_consumed > k_number_of_records_consumed_before_updating_dbpoller):
                    sequence_number = records[-1]['SequenceNumber']
                    dbpoller.update_shard_sequence_number(sequence_number)
                    records_consumed = 0
                    
                    logging.info('update %s sequence number to %s' %(dbpoller.myshard,sequence_number))

            else:
                time.sleep(k_idle_wait_period_to_poll_stream)
                
    else:
        logging.critical ('Failed to initialize because we could not find a free shard.')
    
    
