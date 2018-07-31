from ecc import generateKeyPair, compressPublicKey, generateSignature, verifySignature
from base58check import encode
from block import GenesisBlock

from tx import Tx, TxIn, TxOut

class Node(object):

    def __init__(self, label=None):

        # Labeling
        self.nodeType = "Basic"
        self.label = label

        (sk, pk) = generateKeyPair()
        self.privateKey = sk
        self.uncompressedPublicKey = pk

        cpk = compressPublicKey(pk)
        self.publicKey = cpk
        self.address = encode(cpk)

        self.peers = set()
        self.memPool = []
        self.blocks = {}

        # hardcode the first block into client nodes
        genesis = GenesisBlock()
        self.blocks[genesis.blockHeader.blockHash()] = genesis


    def __str__(self):
        return self.nodeType + " Node: " + self.label or self.address


    def __repr__(self):
        return self.__str__()


    def transfer(self, amount, address):
        uTxs = []
        total = 0

        for (tx, i) in self.unspentOutputs():
            total += tx.outputs[i].amount
            uTxs.append((tx, i))

            if total >= amount:
                break
        else:
            raise ValueError("Wallet dose not have enough spendable outputs for transfer.")

        txIns = []
        for (tx, i) in uTxs:
            txIn = TxIn(tx.toHash(), i)
            txIn.setScriptSig(generateSignature(txIn.toBytes(), self.privateKey), self.publicKey)
            txIns.append(txIn)

        txOuts = [TxOut(amount, address)]

        change = total - amount
        if change > 0:
            txOuts.append(TxOut(change, self.address))

        self.receiveTx(Tx(txIns, txOuts))


    def addPeer(self, peer):
        self.peers.add(peer)


    def receiveTx(self, tx):
        # check if the received tx is valid, if not we can discard it
        if not self.verifyTx(tx):
            return

        # check if the tx is already in the blockchain
        for (_, block) in self.blocks.items():
            for blockTx in block.transactions:
                if blockTx.toHash() == tx.toHash():
                    return

        # check if tx is already in memPool
        if tx in self.memPool:
            return

        self.memPool.append(tx)

        for peer in self.peers:
            peer.receiveTx(tx)


    def receiveBlock(self, block):
        # if block is already known we dont need to rebroadcast it
        if block.blockHeader.blockHash() in self.blocks:
            return

        # add block to our lookup
        self.blocks[block.blockHeader.blockHash()] = block

        # remove transactions from mempool that were added to

        for peer in self.peers:
            peer.receiveBlock(block)


    def currentBlockChain(self):
        currentBlock = self.latestBlock()
        result = []

        while currentBlock is not None:
            result.append(currentBlock)

            prevBlockHash = currentBlock.blockHeader.prevBlockHash
            if int(prevBlockHash.hex(), base=16) == 0:
                break

            currentBlock = self.blocks[prevBlockHash]

        return result


    def latestBlock(self):
        currentHead = None
        currentHeadLen = 0

        for (blockHash, block) in self.blocks.items():

            tempHead = block
            tempHeadLen = 0

            while True:
                tempHeadLen += 1

                prevBlockHash = tempHead.blockHeader.prevBlockHash
                if int(prevBlockHash.hex(), base=16) == 0:
                    break

                tempHead = self.blocks[prevBlockHash]

            if tempHeadLen > currentHeadLen:
                currentHead = block
                currentHeadLen = tempHeadLen

        return currentHead



    def verifyTx(self, tx):
        for txIn in tx.inputs:
            prevTx = None

            # find referenced tx
            for (_, block) in self.blocks.items():
                for tx in block.transactions:
                    if txIn.prevTxHash == tx.toHash():
                        prevTx = tx
                        break

            prevOutput = prevTx.outputs[txIn.prevTxOutIndex]
            intenedAddress = prevOutput.address

            sig = txIn.signature
            publicKey = txIn.publicKey

            pkAddress = encode(publicKey)

            # check intenedAddress of previous output equals address in input
            if pkAddress != intenedAddress:
                return False

            # check the signature verifies the owner of the public key
            if not verifySignature(txIn.toBytes(), sig, publicKey):
                return False

            # check if the outputs have already been used as inputs (double spend)
            # TODO: ...

        return True


    def unspentOutputs(self):
        """returns an array of tuples of (tx, outputIndex)"""
        result = []

        for block in self.currentBlockChain():
            for tx in block.transactions:
                for output in tx.outputs:

                    # find all outputs that are sent to our address
                    if output.address != self.address:
                        continue

                    # to find out if the coin has been spent in following blocks
                    # check if its been used as an input

                    unspent = True

                    for futureBlock in self.currentBlockChain():
                        for futureTx in futureBlock.transactions:
                            for txIn in futureTx.inputs:
                                if txIn.prevTxHash == tx.toHash() and tx.outputs[txIn.prevTxOutIndex] == output:
                                    unspent = False

                        # we dont need to check past here
                        if futureBlock.blockHeader.blockHash() == block.blockHeader.blockHash():
                            break

                    if unspent:
                        result.append((tx, tx.outputs.index(output)))

        return result


    def spendableAmount(self):
        result = 0

        for (tx, i) in self.unspentOutputs():
            result += tx.outputs[i].amount
        return result


def connect(nodeA, nodeB):
    nodeA.addPeer(nodeB)
    nodeB.addPeer(nodeA)
