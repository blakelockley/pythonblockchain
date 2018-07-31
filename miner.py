from hashlib import sha256
from random import random, randint
from node import Node
from block import Block, UnminedBlock

TARGET_SIZE = 256
TARGET_ZEROS = 8

target_binary = '0' * TARGET_ZEROS + '1' * (TARGET_SIZE - TARGET_ZEROS)
target = int(target_binary, base=2)

class Miner(Node):

    def __init__(self, label=None):
        super(Miner, self).__init__(label)
        self.nodeType = "Miner"


    def mine(self, unminedBlock):
        unminedBlock.addRewardTransaction(self.address, len(self.currentBlockChain()))
        header = unminedBlock.incompleteBlockHeader()

        start = randint(0, 2 ** 32 - 1)
        for n in range(2 ** 32):
            nonce = (start + n) % 2 ** 32

            header.setNonce(nonce)
            tempBlockHash = header.blockHash()

            if int(tempBlockHash.hex(), 16) <= target:
                break

        block = Block(unminedBlock.transactions, header)
        self.receiveBlock(block)

        return block


    def mineCurrentMempool(self):
        unmined = UnminedBlock(self.memPool, self.latestBlock().blockHeader.blockHash())
        self.mine(unmined)

        self.memPool = []
