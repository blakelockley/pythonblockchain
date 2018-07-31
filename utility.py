from hashlib import sha256

def paddedBytes(x, nBytes=32):
    return x.to_bytes(nBytes, 'big')
