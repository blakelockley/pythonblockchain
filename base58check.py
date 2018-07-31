from hashlib import sha256, new
from utility import paddedBytes

CODESTRING = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
codeLookup = dict(zip(CODESTRING, range(len(CODESTRING))))

def _base58Encode(hashedAddressBytes):
    n = int(hashedAddressBytes.hex(), base=16)

    result = ''
    while n > 0:
        d, r = n // 58, n % 58
        result += CODESTRING[r]
        n = d

    # append same number of leading zeros as in bytes
    for b in hashedAddressBytes:
        if b != 0:
            break
        result += CODESTRING[0]

    return result[::-1]


def _base58Decode(address):
    result = 0

    for c in address:
        result *= 58
        result += codeLookup[c]

    return paddedBytes(result, 25)


def encode(publicKeyBytes):
    hashed = sha256(publicKeyBytes).digest()

    ripemd160 = new('ripemd160')
    ripemd160.update(hashed)

    hashed = ripemd160.digest()

    # add 0x00 as version code for main network
    hashed = bytes(1) + hashed

    # hash twice with sha256
    checksumHashed = sha256(hashed).digest()
    checksumHashed = sha256(checksumHashed).digest()

    checksum = checksumHashed[:4]
    hashed = hashed + checksum

    return _base58Encode(hashed)


def decode(address):
    hashed = _base58Decode(address)

    payload = hashed[:-4]
    checkSum = hashed[-4:]

    checksumHashed = sha256(payload).digest()
    checksumHashed = sha256(checksumHashed).digest()

    expectedChecksum = checksumHashed[:4]

    if checkSum != expectedChecksum:
        raise ValueError("Checksum dose not match for address.")

    return payload
