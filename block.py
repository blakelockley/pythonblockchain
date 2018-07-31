from hashlib import sha256
from tx import Tx, TxReward

class BlockHeader(object):

    def __init__(self, prevBlockHash, merkleRoot, nonce=None):
        self.prevBlockHash = prevBlockHash
        self.merkleRoot = merkleRoot
        self.nonce = nonce


    def setNonce(self, nonce):
        self.nonce = nonce.to_bytes(4, 'big')


    def blockHash(self):
        return sha256(self.prevBlockHash + self.merkleRoot + self.nonce).digest()


class Block(object):

    def __init__(self, transactions, blockHeader):
        if len(transactions) == 0:
            raise ValueError("A mined block requires at least one transaction.")

        self.transactions = transactions
        self.blockHeader = blockHeader


    def __str__(self):
        return "Block: " + str(self.blockHeader.blockHash().hex())


    def __repr__(self):
        return self.__str__()


    def merkleRoot(self):
        currentList = [tx.toHash() for tx in self.transactions]

        while len(currentList) > 1:
            tempList = []

            for i in range(0, len(currentList) // 2 * 2, 2):
                hashed = sha256(currentList[i] + currentList[i + 1]).digest()
                tempList.append(hashed)

            if len(currentList) % 2 != 0:
                # if odd number of elements hash and append last element
                lastItem = currentList[-1]
                hashed = sha256(lastItem + lastItem).digest()
                tempList.append(hashed)

            currentList = tempList

        return currentList[0]


class UnminedBlock(Block):

    def __init__(self, transactions, prevBlockHash):
        self.transactions = transactions
        self.prevBlockHash = prevBlockHash

        self.reward = 50
        self.rewardTransaction = None


    def addRewardTransaction(self, address, blockHeight):
        if self.rewardTransaction is not None:
            raise ValueError("A block can only contain one reward transaction.")

        tx = TxReward(address, blockHeight)
        self.rewardTransaction = tx
        self.transactions = [tx] + self.transactions


    def incompleteBlockHeader(self):
        if self.rewardTransaction is None:
            raise ValueError("A minable block must contain a reward transaction.")

        return BlockHeader(self.prevBlockHash, self.merkleRoot())


class GenesisBlock(Block):

    # hardcoded

    def __init__(self):
        unmined = UnminedBlock([], bytes(32))
        unmined.addRewardTransaction("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", 0)

        header = unmined.incompleteBlockHeader()
        header.setNonce(3719336634)

        super(GenesisBlock, self).__init__(unmined.transactions, header)
