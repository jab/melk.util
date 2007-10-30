import random
from base64 import b16encode
import md5

def nonce_str(): 
    m = md5.new()
    m.update('%d' % random.getrandbits(128))
    return b16encode(m.digest())
