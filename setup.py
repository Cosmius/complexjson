#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

try:
    import complexjson
except Exception:
    raise NotImplementedError("Sorry you need a simplejson or Python 2.6+ to use"
                              " complexjson. if you have simplejson or "
                              "Python2.6+, Please report a bug")

setup(
    name='complexjson',
    version=complexjson.__version__,
    license='BSD',
    author=complexjson.__author__,
    description='A extending of the python json package',
    long_description=complexjson.__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    py_modules=['complexjson'],
    platform='any',
)