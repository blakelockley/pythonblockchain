from node import Node, connect
from miner import Miner
from utility import paddedBytes

class Interface(object):

    def __init__(self):
        self.relayNode = Node("Interface Relay Node")
        self.nodes = {self.relayNode.label: self.relayNode}


    def newNode(self, label):
        if label in self.nodes:
            raise ValueError("A node labelled '{}' already exists.".format(label))

        newNode = Miner(label)
        newNode.addPeer(self.relayNode) # relayNode will hear but not send out txs/blocks

        self.nodes[label] = newNode


    def newMiner(self, label):
        if label in self.nodes:
            raise ValueError("A node labelled '{}' already exists.".format(label))

        newNode = Miner(label)
        newNode.addPeer(self.relayNode)

        self.nodes[label] = newNode


    def connectNodes(self, labelA, labelB):
        connect(self.nodes[labelA], self.nodes[labelB])


    def send(self, labelA, labelB, amount):
        if labelA == labelB:
            raise ValueError("Cannot connect node to itself.")

        amount = int(amount)
        self.nodes[labelA].transfer(amount, self.nodes[labelB].address)


    def mine(self, label):
        self.nodes[label].mineCurrentMempool()


    def blockchain(self):
        return self.relayNode.currentBlockChain()


    def block(self, blockHash):
        blockHashBytes = paddedBytes(int(blockHash, base=16), 32)
        return self.relayNode.blocks[blockHashBytes]


    def tx(self, txHash):
        txHashBytes = paddedBytes(int(txHash, base=16), 32)

        for (_, block) in self.relayNode.blocks.items():
            for tx in block.transactions:
                if tx.toHash() == txHashBytes:
                    return tx

    def owner(self, address):
        for (_, node) in self.nodes.items():
            if node.address == address:
                return node
