# -*- coding: utf-8 -*-
"""
    complexjson
    ~~~~~~~~~~~

    ComplexJson is a extending of the python json package.

    It provide a json bidirectional converter that acts like the json package.

    :copyright: (c) 2012 by Cosmia Luna http://blog.cosmius.com/
    :license: BSD, see LICENSE for more details.

    see README for usage.
"""
__version__ = '0.1'
__author__ = 'Cosmia Luna'
try:
    import simplejson as json
except ImportError:
    import json
from UserDict import DictMixin


class JSONConverter(object):

    __encoder_kws = ('skipkeys', 'ensure_ascii', 'check_circular', 'allow_nan',
                     'sort_keys', 'indent', 'separators')
    __decoder_kws = ('parse_float', 'parse_int', 'parse_constant', 'strict')

    json_version = json.__version__

    def __init__(self, encoding='utf-8', default=None, object_hook=None,
                 type_key='__type__', data_key = '__data__',
                 json_key = '__json__', **options):
        encoder_args = {}
        decoder_args = {}
        for name in self.__encoder_kws:
            if name in options:
                encoder_args[name] = options.pop(name)
        for name in self.__decoder_kws:
            if name in options:
                decoder_args[name] = options.pop(name)
        if len(options) > 0:
            raise TypeError('Unknown keywords argument: {0}'.format(
                ', '.join(options.iterkeys())))
        encoder_args['encoding'] = decoder_args['encoding'] = encoding

        self.__types = BidirectionalDict()
        self.types = ()
        self.type_key = type_key
        self.data_key = data_key
        self.json_key = json_key
        self.hook_set = set((type_key, data_key))

        if default is None:
            def default(o):
                raise TypeError(repr(o) + " is not JSON serializable")
        self.default = default

        self.object_hook = object_hook or (lambda x: x)

        encoder_args['default'] = self.encode_type
        decoder_args['object_hook'] = self.decode_type

        self.encoder = json.JSONEncoder(**encoder_args)
        self.decoder = json.JSONDecoder(**decoder_args)

    def register(self, key_or_cls, cls=None):
        key = key_or_cls
        if cls is None:
            if not isinstance(key_or_cls, type):
                def decorator(cls):
                    self.register(key, cls)
                    return cls
                return decorator
            else:
                cls = key_or_cls
                key = cls.__module__ + '.' + cls.__name__

        if not hasattr(cls, self.json_key):
            msg = "type must have {0} method defined".format(self.json_key)
            raise TypeError(msg)
        self.__types.setitem(key, cls)
        return cls

    def freeze(self):
        self.types = tuple(self.__types.rkeys())
        def freezed_register(key_or_cls, cls=None):
            msg = "This converter is freezed, nothing is done"
            from warnings import warn
            warn(msg, stacklevel=2)
            if cls is None:
                return key_or_cls
            return cls
        self.register = freezed_register

    def encode_type(self, o):
        cls = type(o)
        if cls not in self.types:
            return self.default(o)
        return {self.type_key: self.__types.rget(cls),
                self.data_key: getattr(cls, self.json_key)(o)}

    def decode_type(self, d):
        if set(d) != self.hook_set:
            # call custom object_hook
            return self.object_hook(d)
        type_idx = d[self.type_key]
        data = d[self.data_key]
        cls = self.__types.lget(type_idx)
        return getattr(cls, self.json_key)(data)

    def encode(self, o):
        return self.encoder.encode(o)
    dumps = encode

    def iterencode(self, o):
        return self.encoder.iterencode(o)

    def decode(self, s):
        return self.decoder.decode(s)
    loads = decode

    def dump(self, o, fp):
        for chunk in self.iterencode(o):
            fp.write(chunk)
    def load(self, fp):
        return self.loads(fp.read())


class BidirectionalDict(object, DictMixin):
    def __init__(self, *a, **kw):
        kw.update(*a)
        self.__l2r = {}
        self.__r2l = {}
        self.update(kw)

    def copy(self):
        return type(self)(self)

    def lget(self, lv):
        return self.__l2r[lv]
    def rget(self, rv):
        return self.__r2l[rv]

    def setitem(self, lv, rv):
        """returns True if conflict found, or False if no conflict"""
        if not (hasattr(lv, '__hash__') and hasattr(rv, '__hash__')):
            raise TypeError("lv and rv must be hashable")
        if lv is None or rv is None:
            raise TypeError("lv and rv cannot be None")
        conflict = self.__l2r.pop(lv, None) is not None
        conflict = (self.__r2l.pop(rv, None) is not None) or conflict
        self.__l2r[lv] = rv
        self.__r2l[rv] = lv
        return conflict

    def _pop(self, lv, rv, *a):
        if rv is None:
            original = self.__l2r
            referenced = self.__r2l
            key = lv
        else:
            original = self.__r2l
            referenced = self.__l2r
            key = rv

        try:
            target = original.pop(key)
        except KeyError:
            if not a:
                raise
            return a[0]
        else:
            del referenced[target]
            return target
    def lpop(self, lv, *a):
        return self._pop(lv, None, *a)
    def rpop(self, rv, *a):
        return self._pop(None, rv, *a)

    def lkeys(self):
        return self.__l2r.keys()
    def rkeys(self):
        return self.__r2l.keys()

    def iteritems(self):
        return self.__l2r.iteritems()

    def lhas(self, lv):
        return lv in self.__l2r
    def rhas(self, rv):
        return rv in self.__r2l

    def __iter__(self):
        return iter(self.__l2r)

    def __contains__(self, lv):
        return self.lhas(lv)

    def _parse_slice(self, k):
        """returns (lv, rv) tuple, with a None and a not None"""
        if not isinstance(k, slice):
            return k, None
        if k.step is None:
            lv, rv = k.start, k.stop
            if (lv is not None and rv is None) or \
                    (lv is None and rv is not None):
                return lv, rv
        msg = ('BidirectionalDict only accept slices like d[lv:] -> rv or '\
            'd[:rv] -> rv, got [{0}:{1}:{2}]').format(k.start, k.stop, k.step)
        raise TypeError(msg)

    def __getitem__(self, k):
        lv, rv = self._parse_slice(k)
        if rv is None:
            return self.lget(lv)
        else:
            return self.rget(rv)

    def __setitem__(self, k, v):
        lv, rv = self._parse_slice(k)
        if rv is None:
            rv = v
        else:
            lv = v
        self.setitem(lv, rv)

    def __delitem__(self, k):
        lv, rv = self._parse_slice(k)
        if rv is None:
            self.lpop(lv)
        else:
            self.rpop(rv)

    def keys(self):
        return self.lkeys()

    def __repr__(self):
        return 'BidirectionalDict({0})'.format(repr(self.__l2r))

