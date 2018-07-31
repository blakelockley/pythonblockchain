from node import Node, connect
from miner import Miner
from utility import paddedBytes

class Interface(object):

    def __init__(self):
        self.relayNode = Node("relay")
        self.nodes = {self.relayNode.label: self.relayNode}


    def newNode(self, label):
        if label in self.nodes:
            raise ValueError("A node labelled '{}' already exists.".format(label))
        self.nodes[label] = Node(label)

    def newMiner(self, label):
        if label in self.nodes:
            raise ValueError("A node labelled '{}' already exists.".format(label))
        self.nodes[label] = Miner(label)


    def connectNodes(self, labelA, labelB):
        if labelA not in self.nodes:
            raise ValueError("No node labeled {}".format(labelA))

        if labelB not in self.nodes:
            raise ValueError("No node labeled {}".format(labelB))

        if labelA == labelB:
            raise ValueError("Cannot connect node to itself.")

        connect(self.nodes[labelA], self.nodes[labelB])


    def send(self, labelA, labelB, amount):
        if labelA not in self.nodes:
            raise ValueError("No node labeled {}".format(labelA))

        if labelB not in self.nodes:
            raise ValueError("No node labeled {}".format(labelB))

        if labelA == labelB:
            raise ValueError("Cannot connect node to itself.")

        self.nodes[labelA].transfer(int(amount), self.nodes[labelB].address)


    def mine(self, label):
        if label not in self.nodes:
            raise ValueError("No node labeled {}".format(label))

        self.nodes[label].mineCurrentMempool()


    def blockchain(self, label):
        if label not in self.nodes:
            raise ValueError("No node labeled {}".format(label))

        return self.nodes[label].currentBlockChain()

    def block(self, label, blockHash):
        if label not in self.nodes:
            raise ValueError("No node labeled {}".format(label))

        blockHashBytes = paddedBytes(int(blockHash, base=16), 32)

        return self.nodes[label].blocks[blockHashBytes]

    def tx(self, label, txHash):
        if label not in self.nodes:
            raise ValueError("No node labeled {}".format(label))

        txHashBytes = paddedBytes(int(txHash, base=16), 32)

        for (_, block) in self.nodes[label].blocks.items():
            for tx in block.transactions:
                if tx.toHash() == txHashBytes:
                    return tx
