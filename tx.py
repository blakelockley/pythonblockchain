from utility import paddedBytes
from hashlib import sha256
from base58check import encode

REWARD_AMOUNT = 50

class TxIn(object):

    def __init__(self, prevTxHash, prevTxOutIndex):
        self.prevTxHash = prevTxHash
        self.prevTxOutIndex = prevTxOutIndex


    def setScriptSig(self, sig, publicKey):
        self.signature = sig
        self.publicKey = publicKey


    def toBytes(self):
        return self.prevTxHash + paddedBytes(self.prevTxOutIndex, 4)


    def toHash(self):
        return sha256(self.toBytes()).digest()


class TxOut(object):

    def __init__(self, amount, address):
        self.amount = amount
        self.address = address # ScriptPubKey


    def __str__(self):
        return "TxOut: {} -> {}".format(self.amount, self.address)


    def __repr__(self):
        return self.__str__()


    def toBytes(self):
        return paddedBytes(self.amount, 8) + self.address.encode()


    def toHash(self):
        return sha256(self.toBytes()).digest()


class Tx(object):

    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def toBytes(self):
        result = bytes(0)
        for ba in map(lambda txIn: txIn.toBytes(), self.inputs):
            result += ba
        for ba in map(lambda txOut: txOut.toBytes(), self.outputs):
            result += ba
        return result

    def toHash(self):
        return sha256(self.toBytes()).digest()

    def __str__(self):
        return 'Tx: ' + self.toHash().hex()

    def __repr__(self):
        return self.__str__()


class TxReward(Tx):

    def __init__(self, address, blockHeight):
        self.blockHeight = blockHeight
        super(TxReward, self).__init__([], [TxOut(REWARD_AMOUNT, address)])


    def toHash(self):
        return sha256(self.toBytes() + paddedBytes(self.blockHeight)).digest()
