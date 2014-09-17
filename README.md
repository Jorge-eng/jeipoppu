jeipoppu
========

J-Pop - annoying anime music, or in our case, server-side audio features processing.

Uses: Amazon Kinesis, DynamoDB

* Client (whether it be Morpheus, a laptop, an app, etc.) pushes audio feature data to our server, and our server puts it the Kinesis "audio_features" stream. 
* AudioFeaturesConsumer.py polls the stream, processes the audio features (i.e. runs a classifier on it), and puts it into the "audio_products" stream
* Someone (unknown who or what right now) will aggregate the audio_products stream and then ship it off to S3, or wherever 


————————

AudioFeaturesConsumer.py


Kinesis stream is divided into shards, each shard should have one processor of a type.
- Let’s say I have a classifier for snoring, and a classifier for dog barking, and for whatever reason they’re not in the same neural net/SVM/whatever so I am running two separate processors.
- Each Kinesis “shard” gets one processor of each type


STREAM
                              
|item1|     |
|     |item2|
|-----|     |
|     |-----|
|item3|     |
|     |item4|
|     |-----|
|-----|     |
|     |     |
|     |     |
|     |     |
|     |     |
 shard shard 
   1     2   
             

shard1 ---> bark processor, node1
       ---> snore processor, node2

shard2 ---> bark processor, node3
       ---> snore processor, node4

-There is a configuration file which will determine what happens in the processor. 
-For example, what processor is used, logging options, which Amazon region, etc.

