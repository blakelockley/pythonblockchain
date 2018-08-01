import sys
from interface import Interface

commands = {}

# interface object to control our network
interface = Interface()

def quit(args):
    exit(0)


def printHelp(args):
    for (command, (description, _)) in commands.items():
        print(command, description)


def new(args):

    if len(args) < 2:
        print("'new' command requires 'nodeType' and 'label' arguments.")
        return

    nodeType    = args[0]
    label       = args[1]

    if nodeType.lower() == 'miner':
        try:
            interface.newMiner(label)
            print("New miner node '{}' created.".format(label))
        except ValueError as e:
            print(e)

    elif nodeType.lower() == 'node' or nodeType.lower() == 'basic':
        try:
            interface.newNode(label)
            print("New node '{}' created.".format(label))
        except ValueError as e:
            print(e)

    else:
        print("No node created. 'nodeType' must be 'miner' or 'basic'/'node'.")


def printAll(args):
    count = len(interface.nodes)
    if count == 0:
        print("No nodes currently exist.")
    else:
        print("Showing {} node(s).".format(count))

    for (_, node) in interface.nodes.items():
        print(node)


def showNode(args):
    if len(args) < 1:
        print("'show' command requires a 'label' argument.")
        return

    label = args[0]

    try:
        node = interface.nodes[label]
    except KeyError:
        print("No node labeled '{}.".format(label))
        return

    print("Showing:", node)
    print("Address:", node.address)
    print("Spendable Amount:", node.spendableAmount())
    print("Peers: ")
    for peer in node.peers:
        print("-", peer)


def connect(args):
    if len(args) < 2:
        print("'connect' command requires two nodes ('label') arguments.")
        return

    try:
        interface.connectNodes(*args)
    except ValueError as e:
        print(e)
        return

    print("Nodes connected: '{}' '{}'.".format(args[0], args[1]))


def load(args):
    if len(args) < 1:
        print("'load' command requires 'scriptName' argument.")
        return

    scriptName = args[0]

    # remove code duplication
    with open(scriptName) as f:
        for lineIn in f:
            try:
                lineInWords = lineIn.strip("\n").split(" ")

                command = lineInWords[0]
                args    = lineInWords[1:]

                if command == '' or command == '#':
                    continue

                (_, func) = commands[command]
                func(args)

            except KeyError:
                print("Unkown command. Try typing 'help' for list of commands.")

    # print("Loaded script '{}'.".format(scriptName))


def send(args):
    if len(args) < 3:
        print("'send' command requires '<labelA>' '<labelB>' <amount> arguments.")
        return

    interface.send(*args)
    print("Amount {} sent from '{}' to '{}'".format(args[2], *args[:2]))


def mine(args):
    if len(args) < 1:
        print("'mine' command requires '<label>' argument.")
        return

    interface.mine(*args)
    print("New block mined by '{}'.".format(*args))


def blockchain(args):
    print("Showing current blockchain.")
    for block in interface.blockchain():
        print(block)


def block(args):
    if len(args) < 1:
        print("'block' command requires '<blockHash>' argument.")
        return

    block = interface.block(*args)

    print(block)
    print("Transactions:")
    for tx in block.transactions:
        print("-", tx)


def tx(args):
    if len(args) < 1:
        print("'tx' command requires '<txHash>' argument.")
        return

    tx = interface.tx(*args)

    print(tx)
    print("Inputs:")
    for txIn in tx.inputs:
        print("-", txIn)
    print("Outputs:")
    for txOut in tx.outputs:
        print("-", txOut)


def owner(args):
    if len(args) < 1:
        print("'tx' command requires '<address>' argument.")
        return

    node = interface.owner(*args)

    print(node.label)


def main(args):
    print("Python Blockchain REPL v0.1")
    print("Type 'help' for list of commands.")
    print("Type 'quit' to exit.")

    # command, description, method
    commands["quit"]    = ("Exit from REPL.",                           quit)
    commands["help"]    = ("List all commands.",                        printHelp)
    commands["new"]     = ("<nodeType> <label> Create a new node.",     new)
    commands["all"]     = ("Print all existing nodes.",                 printAll)
    commands["show"]    = ("<label> Show details of particular node.",  showNode)
    commands["connect"] = ("<labelA> <labelB> Connect two peers in the network.", connect)
    commands["load"]    = ("<scriptName> Load script.",                 load)
    commands["send"]    = ("<labelA> <labelB> <amount> Pay <amount> from one node to an other.", send)
    commands["mine"]    = ("<label> Mine current mempool.",             mine)
    commands["blockchain"] = ("Display the current blockchain.",        blockchain)
    commands["block"]   = ("<blockHash> Display the block of with given hash for a node. ", block)
    commands["tx"]      = ("<txHash> Display the transaction of a given hash for a node.", tx)
    commands["owner"]   = ("<address> Display node owning given address.", owner)

    while True:
        lineIn = input("> ")

        lineInWords = lineIn.split(" ")
        command = lineInWords[0]
        args    = lineInWords[1:]

        try:
            (_, func) = commands[command]
        except KeyError:
            print("Unkown command. Try typing 'help' for list of commands.")
            continue

        try:
            func(args)
        except Exception as e:
            print(e)
            # raise e


if __name__ == "__main__":
    main(sys.argv)
