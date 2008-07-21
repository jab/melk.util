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

import base64
import random
import re
import sha
from struct import pack

try:
    from hashlib import md5 # python2.5
except ImportError:
    from md5 import md5 # python 2.4

__all__ = ['salty_hash', 'salty_hash_matches']

def salty_hash(input, salt=None):
    """
    compute the salty hash of the input given, 
    if no salt is specified a random value is 
    used.
    """
    if salt is None:
        salt = pack('L', random.getrandbits(32))
        salt = base64.b64encode(salt)

    hasher = sha.new()
    hasher.update(salt)
    hasher.update(input)
    return '%s:%s' % (salt, base64.b64encode(hasher.digest()))
    
def salty_hash_matches(input, hash):
    """
    @returns True if the salty hash of input matches the 
    hash given (using the same salt as the hash given)
    """
    salt, xx = hash.split(':')
    return salty_hash(input, salt) == hash


MELK_ID_PAT = re.compile(r'melk\:[\d,a-f]{8}-[\d,a-f]{4}-[\d,a-f]{4}-[\d,a-f]{4}-[\d,a-f]{12}\Z')
def is_melk_id(mid): 
    return MELK_ID_PAT.match(mid) is not None

def melk_id(iid, source=None):
    hash = md5()
    hash.update(iid)
    if source is not None:
        hash.update(source)

    hex = hash.hexdigest()
    
    return 'melk:%s-%s-%s-%s-%s' % (hex[0:8], hex[8:12], hex[12:16], 
                                    hex[16:20], hex[20:32])

def main(): 
    import sys
    if len(sys.argv) != 2:
        print 'usage: %s <password>' % sys.argv[0]
        sys.exit(0)

    print salty_hash(sys.argv[1])
