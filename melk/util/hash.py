import random
import sha
import base64

__all__ = ['salty_hash', 'salty_hash_matches']

def salty_hash(input, salt=None):
    """
    compute the salty hash of the input given, 
    if no salt is specified a random value is 
    used.
    """
    if salt is None:
        # random.getrandbits(32) ? how -> str?? 
        salt = ''
        for i in range(4): 
            salt += chr(random.randrange(0,255))
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

def main(): 
    import sys
    if len(sys.argv) != 2:
        print 'usage: %s <password>' % sys.argv[0]
        sys.exit(0)

    print salty_hash(sys.argv[1])
