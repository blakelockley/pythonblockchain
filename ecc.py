# Adaptation of code by James D'Angelo (wobine):
# https://github.com/wobine/blackboard101/blob/master/EllipticCurvesPart4-PrivateKeyToPublicKey.py
# https://www.youtube.com/watch?v=iB3HcPgm_FI

Pcurve = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 -1 # The proven prime
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 # Number of points in the field
Acurve = 0; Bcurve = 7 # These two defines the elliptic curve. y^2 = x^3 + Acurve * x + Bcurve
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
GPoint = (Gx,Gy) # This is our generator point. Trillions of dif ones possible

def modinv(a,n=Pcurve): #Extended Euclidean Algorithm/'division' in elliptic curves
    lm, hm = 1,0
    low, high = a%n,n
    while low > 1:
        ratio = high//low # / changed to // for python3
        nm, new = hm-lm*ratio, high-low*ratio
        lm, low, hm, high = nm, new, lm, low
    return lm % n

def EccAdd(a,b): # Not true addition, invented for EC. Could have been called anything.
    LamAdd = ((b[1]-a[1]) * modinv(b[0]-a[0],Pcurve)) % Pcurve
    x = (LamAdd*LamAdd-a[0]-b[0]) % Pcurve
    y = (LamAdd*(a[0]-x)-a[1]) % Pcurve
    return (x,y)

def EccDouble(a): # This is called point doubling, also invented for EC.
    Lam = ((3*a[0]*a[0]+Acurve) * modinv((2*a[1]),Pcurve)) % Pcurve
    x = (Lam*Lam-2*a[0]) % Pcurve
    y = (Lam*(a[0]-x)-a[1]) % Pcurve
    return (x,y)

def EccMultiply(GenPoint,ScalarHex): #Double & add. Not true multiplication
    if ScalarHex == 0 or ScalarHex >= N: raise Exception("Invalid Scalar/Private Key")
    ScalarBin = str(bin(ScalarHex))[2:]
    Q=GenPoint
    for i in range (1, len(ScalarBin)): # This is invented EC multiplication.
        Q=EccDouble(Q); # print "DUB", Q[0]; print
        if ScalarBin[i] == "1":
            Q=EccAdd(Q,GenPoint); # print "ADD", Q[0]; print
    return (Q)


# Custom code using the eliptic curve

import random
from hashlib import sha256
from utility import paddedBytes

# generate keys

def generatePrivateKey():
    """private key as a 32 sized byte array"""

    privateKey = random.getrandbits(256)
    return paddedBytes(privateKey, 32)


def generatePublicKey(privateKeyBytes):
    """uncompressed public key, 65 sized byte array, starting with 04 followed by the x and y coord"""

    privateKeyValue = int(privateKeyBytes.hex(), 16)
    publicKeyPoint = EccMultiply(GPoint, privateKeyValue)
    (x, y) = publicKeyPoint
    return paddedBytes(4, 1) + paddedBytes(x, 32) + paddedBytes(y, 32)


def generateKeyPair():
    """return private key 32 bytes and uncompressed publicKey 65 bytes"""
    privateKeyBytes = generatePrivateKey()
    publicKeyBytes = generatePublicKey(privateKeyBytes)

    return (privateKeyBytes, publicKeyBytes)

# public key functions

def compressPublicKey(publicKeyBytes):
    """compressed public key is 33 bytes starting with 02 or 03"""

    if (len(publicKeyBytes) != 65 or publicKeyBytes[0] != 4):
        raise ValueError("Uncompressed public key must start with 04 byte followed by 64 bytes.")

    xBytes = publicKeyBytes[1:33]
    yBytes = publicKeyBytes[33:]

    leadingByte = paddedBytes(2 + int(yBytes.hex(), base=16) % 2, 1)
    return leadingByte + xBytes


def uncompressPublicKey(compressedPublicKeyBytes):
    if (len(compressedPublicKeyBytes) != 33):
        raise ValueError("Compressed public key must be 33 bytes long.")

    leadingByte = compressedPublicKeyBytes[0]

    if (leadingByte != 2 and leadingByte != 3):
        raise ValueError("Leading byte of compressed public key must begin with 02 or 03 byte.")

    x = int(compressedPublicKeyBytes[1:].hex(), base=16)
    y_square = (pow(x, 3, Pcurve) + Bcurve) % Pcurve

    # https://stackoverflow.com/questions/43629265/deriving-an-ecdsa-uncompressed-public-key-from-a-compressed-one/43654055
    y_sq_sq_rt = pow(y_square, (Pcurve + 1) // 4, Pcurve)

    # if leadingByte and odd/evenness  do not match we negate y_sq_sq_rt
    if ((leadingByte == 2 and y_sq_sq_rt % 2 == 1) or (leadingByte == 3 and y_sq_sq_rt % 2 == 0)):
        y = (-y_sq_sq_rt) % Pcurve
    else:
        y = y_sq_sq_rt

    return paddedBytes(4, 1) + paddedBytes(x, 32) + paddedBytes(y, 32)


def publicKeyPoint(publicKeyBytes):
    if (len(publicKeyBytes) != 33 and len(publicKeyBytes) != 65):
        raise ValueError("Public key must be 33 or 65 bytes long.")

    leadingByte = publicKeyBytes[0]
    if (leadingByte == 2 or leadingByte == 3):
        uncompressed = uncompressPublicKey(publicKeyBytes)
    elif  (leadingByte == 4):
        uncompressed = publicKeyBytes
    else:
        raise ValueError("Public key must start with 02, 03 or 04 byte.")

    x = int(uncompressed[1:33].hex(), base=16)
    y = int(uncompressed[33:].hex(), base=16)

    return (x, y)

# signing and verifiying

def generateSignature(messageBytes, privateKeyBytes):
    randomN = random.getrandbits(256)
    (rx, _) = EccMultiply(GPoint, randomN)
    r = rx % N

    messageHash = sha256(messageBytes).digest()
    messageValue = int(messageHash.hex(), base=16)

    privateKey = int(privateKeyBytes.hex(), base=16)
    sigFactor = ((messageValue + r * privateKey) * modinv(randomN, N)) % N

    return (sigFactor, r)


def verifySignature(messageBytes, signature, publicKeyBytes):
    messageHash = sha256(messageBytes).digest()
    messageValue = int(messageHash.hex(), base=16)

    sigFactor, r = signature
    pk = publicKeyPoint(publicKeyBytes)

    w = modinv(sigFactor, N)
    u1 = EccMultiply(GPoint, (messageValue * w) % N)
    u2 = EccMultiply(pk, (r * w) % N)

    (x, _) = EccAdd(u1, u2)

    return x == r
