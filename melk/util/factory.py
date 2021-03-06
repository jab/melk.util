# Copyright (C) 2007 The Open Planning Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

from melk.util.objecturi import parse_object_uri
import cgi
import logging
import traceback

log = logging.getLogger(__name__)


def _validated(function, schema): 
    """ 
    returns a callable that calls the function 
    given with the results of passing the 
    formencode schema given over the arguments
    passed to the callable.
    """
    def vf(**kwargs):
        args = schema.to_python(kwargs)
        return function(**args)
    return vf

class BasicFactory(object): 
    """
    """
    def __init__(self): 
        self._constructors = {}

    def create(self, uri, **kwargs): 
        # find a constructor for uri
        ctor_info = self._constructors.get(uri, None)
        if ctor_info is None:
            return None
        else:
            ctor, args = ctor_info
            args.update(kwargs)

            # try to construct the object
            log.debug("Creating object %s args=%s" % (uri, args))
            return ctor(**args)

    def register(self, uri, constructor, schema=None, defaults=None):
        """
        @param uri - identifier for the object being registered
        @param constructor - a function used to construct the filter specified
        @param schema - an optional formencode schema to validate / parse the 
        arguments to the constructor
        @param defaults - an optional dictionary of default constructor arguments
        """
        if defaults is None:
            defaults = {}

        # wrap the constructor in a schema validation if a
        # schema was specified
        if schema is not None:
            constructor = _validated(constructor, schema)
            
        log.debug("Registering constructor for %s" % uri)

        self._constructors[uri] = (constructor, dict(defaults))

class BasicObjectURIFactory(BasicFactory): 
    
    def create_from_uri(self, object_uri):
        """
        """
        # break the object_uri into a base_uri and the
        # constructor arguments
        base_uri, raw_args = parse_object_uri(object_uri)
        uri_args = dict([(arg[0].encode('ascii'), arg[1]) for arg in raw_args.items()])
        return self.create(base_uri, **uri_args)

    def register(self, uri, constructor, schema=None, defaults=None): 
        # normalize and separate off any arguments
        base_uri, args = parse_object_uri(uri)
        return BasicFactory.register(self, base_uri, constructor,
                                     schema, defaults)

