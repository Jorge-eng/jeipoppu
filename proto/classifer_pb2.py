# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: classifer.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='classifer.proto',
  package='',
  serialized_pb='\n\x0f\x63lassifer.proto\"\xe1\x01\n\x10\x61udio_class_data\x12\x13\n\x0bprobability\x18\x01 \x03(\x02\x12.\n\x07\x63lasses\x18\x02 \x03(\x0e\x32\x1d.audio_class_data.audio_class\x12/\n\x08\x64\x65\x63ision\x18\x03 \x01(\x0e\x32\x1d.audio_class_data.audio_class\"W\n\x0b\x61udio_class\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04NULL\x10\x01\x12\x0b\n\x07TALKING\x10\x02\x12\n\n\x06\x43RYING\x10\x03\x12\x0b\n\x07SNORING\x10\x04\x12\x0b\n\x07VEHICLE\x10\x05\"\xdd\x01\n\x1b\x61udio_classifcation_message\x12\x10\n\x08\x66\x65\x61t_vec\x18\x01 \x03(\x02\x12)\n\x0e\x63lassification\x18\x02 \x01(\x0b\x32\x11.audio_class_data\x12\r\n\x05time1\x18\x03 \x01(\x03\x12\r\n\x05time2\x18\x04 \x01(\x03\x12\x11\n\tunix_time\x18\x05 \x01(\x05\x12\x15\n\rclassifer_key\x18\x06 \x01(\t\x12\x0c\n\x04tags\x18\x07 \x01(\t\x12\x0e\n\x06source\x18\x08 \x01(\t\x12\x0b\n\x03mac\x18\t \x01(\x0c\x12\x0e\n\x06userid\x18\n \x01(\t')



_AUDIO_CLASS_DATA_AUDIO_CLASS = _descriptor.EnumDescriptor(
  name='audio_class',
  full_name='audio_class_data.audio_class',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NULL', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TALKING', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CRYING', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SNORING', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VEHICLE', index=5, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=158,
  serialized_end=245,
)


_AUDIO_CLASS_DATA = _descriptor.Descriptor(
  name='audio_class_data',
  full_name='audio_class_data',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='probability', full_name='audio_class_data.probability', index=0,
      number=1, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='classes', full_name='audio_class_data.classes', index=1,
      number=2, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='decision', full_name='audio_class_data.decision', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _AUDIO_CLASS_DATA_AUDIO_CLASS,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=20,
  serialized_end=245,
)


_AUDIO_CLASSIFCATION_MESSAGE = _descriptor.Descriptor(
  name='audio_classifcation_message',
  full_name='audio_classifcation_message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='feat_vec', full_name='audio_classifcation_message.feat_vec', index=0,
      number=1, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='classification', full_name='audio_classifcation_message.classification', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='time1', full_name='audio_classifcation_message.time1', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='time2', full_name='audio_classifcation_message.time2', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='unix_time', full_name='audio_classifcation_message.unix_time', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='classifer_key', full_name='audio_classifcation_message.classifer_key', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tags', full_name='audio_classifcation_message.tags', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='audio_classifcation_message.source', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mac', full_name='audio_classifcation_message.mac', index=8,
      number=9, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userid', full_name='audio_classifcation_message.userid', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=248,
  serialized_end=469,
)

_AUDIO_CLASS_DATA.fields_by_name['classes'].enum_type = _AUDIO_CLASS_DATA_AUDIO_CLASS
_AUDIO_CLASS_DATA.fields_by_name['decision'].enum_type = _AUDIO_CLASS_DATA_AUDIO_CLASS
_AUDIO_CLASS_DATA_AUDIO_CLASS.containing_type = _AUDIO_CLASS_DATA;
_AUDIO_CLASSIFCATION_MESSAGE.fields_by_name['classification'].message_type = _AUDIO_CLASS_DATA
DESCRIPTOR.message_types_by_name['audio_class_data'] = _AUDIO_CLASS_DATA
DESCRIPTOR.message_types_by_name['audio_classifcation_message'] = _AUDIO_CLASSIFCATION_MESSAGE

class audio_class_data(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _AUDIO_CLASS_DATA

  # @@protoc_insertion_point(class_scope:audio_class_data)

class audio_classifcation_message(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _AUDIO_CLASSIFCATION_MESSAGE

  # @@protoc_insertion_point(class_scope:audio_classifcation_message)


# @@protoc_insertion_point(module_scope)