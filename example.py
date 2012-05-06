# -*- coding: utf-8 -*-

from complexjson import JSONConverter

# Initialize the JSONConverter
options = {}
json = JSONConverter(type_key='__type__', data_key = '__data__',
                     json_key = '__json__', **options)

# JSONConverter accept similar argument as json in the standard library does.
# usually the default works fine. The following is the list of argument

# This is argument for JSON encoder, refer Python Documentation for more
encoder_kws = ('skipkeys', 'ensure_ascii', 'check_circular', 'allow_nan',
               'sort_keys', 'indent', 'separators', 'default')

# This is argument for JSON decoder, refer Python Documentation for more
decoder_kws = ('parse_float', 'parse_int', 'parse_constant', 'strict',
               'object_hook')

# And the encoding argument used for both Encoder and Decoder

# the type_key is the key stores type information in the dumped json,
# the data_key is the key stores real data in the dumped json,
# also, a json object with only type_key, data_key defined will be considered to
# be decoded using the custom ways
# json_key is the method name to be called when dumping or loading,
# described below

@json.register
class SomeType(object):
    def __init__(self, **kwds):
        # do somthing to construct the object
        pass

    @classmethod
    def __json__(cls, obj_or_data):
        if type(obj_or_data) is cls:
            obj = obj_or_data
            # return a json serializable version of obj
            return dict(obj.__dict__) # or something others
        else:
            data = obj_or_data
            new_obj = cls(**data)
            return new_obj # or reconstruct the object via other method
# and the __json__ method must meet the following condition

data = {} # assume data is arbitrary object that is possible from __json__ 
obj = SomeType() # assume obj is arbitrary SomeType object

assert obj  == SomeType.__json__( SomeType.__json__(obj ) )
assert data == SomeType.__json__( SomeType.__json__(data) )


# when you registered all your types you must call json.freeze() method
json.freeze()

# now you can use json as the usual json module with dumps, loads, dump, load
# defined but with only limited arguments since the argument moves to the
# JSONConverter.__init__. Method encode and decode are also defined

jsonfied = json.dumps(obj)
reconstructed = json.loads(jsonfied)

# iterencode is also defined

from io import BytesIO
bytesI = BytesIO()
for chunk in json.iterencode(obj):
    bytes.write(chunk)






























