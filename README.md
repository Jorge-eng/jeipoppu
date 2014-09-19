jeipoppu
========

J-Pop - annoying anime music, or in our case, server-side audio features processing.

Uses: Amazon Kinesis, DynamoDB

* Client (whether it be Morpheus, a laptop, an app, etc.) pushes audio feature data to our server, and our server puts it the Kinesis "audio_features" stream. 
* AudioFeaturesConsumer.py polls the stream, processes the audio features (i.e. runs a classifier on it), and puts it into the "audio_products" stream
* Someone (unknown who or what right now) will aggregate the audio_products stream and then ship it off to S3, or wherever 
* Config file determines everything... which S3 bucket/key to pull the classifier from, which classifier to use, which streams, etc.
* Execution: ./AudioFeaturesConsumer.py ./config.txt
--------------

Example of The Data Model
--------------------------

Kinesis stream is divided into shards, each shard should have one processor of a type.
- Let’s say I have a classifier for snoring, and a classifier for dog barking, and for whatever reason they’re not in the same neural net/SVM/whatever so I am running two separate processors.
- Each Kinesis “shard” gets one processor of each type


                              
STREAM: audio_features <br/>
&nbsp;&nbsp;&nbsp;---> shard1<br/>
&nbsp;&nbsp;&nbsp;---> shard2<br/>           
<br/>
 shard1 <br/>
&nbsp;&nbsp;&nbsp;---> bark processor, node1<br/>
&nbsp;&nbsp;&nbsp; ---> snore processor, node2<br/>

 shard2 <br/>
&nbsp;&nbsp;&nbsp;---> bark processor, node3<br/>
&nbsp;&nbsp;&nbsp;---> snore processor, node4<br/>
<br/>

node1,node2,node3,node4 ----> STREAM: audio_products<br/>


protobufs  
---------------------
* audio_features stream uses the "matrix.proto" message definitions, which is define in the kitsune repo (kitsune/kitsune/protobuf)  
* audio_products stream uses the "classifiers.proto" message definitions, which is defined in the ./proto directory 
* ALL CLASSIFIER CLASS LABELS ARE DEFINED IN THE classifiers.proto DEFINITION.  I.e. class label SNORING is audio_class_data.audio_class.SNORING
* Everyone has access to the protobuf messages, it's backwards compatible... lots of good reasons to use it.
