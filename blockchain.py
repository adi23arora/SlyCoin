	######################################### 
	#										#
	# Implementation of Basic Blockchain	#
	#										#
	#########################################

import hashlib
import json
from time import time

from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask,jsonify,request



class Blockchain(object):


	def __init__(self):
        
        self.chain = []
        self.current_transactions = []


        # Creating the Genesis block
        self.new_block(previous_hash=1, proof=100)



    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })

        return self.last_block['index']+1


    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        
        :param block: <dict> Block
        :return: <str> string after hashing
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()



    @property
    def last_block(self):
        return self.chain[-1]



    # For bitcoin its (PoW Algo) called as HashCash
    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        
        :param last_proof: <int>
        :return: <int>
        """
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1

        return proof



    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        # Difficulty of Algorithm can be adjusted by modifying no. of leading zeros which are 4 in this case




    def validate_chain():
         """
        Determine if a given blockchain is valid
        
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index != len(chain)
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print(f'{\n-------------------\n}')

            # Check that the hash of block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Checking for correctness of Proof of Work
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True



    # For the Consensus Algo. to maintain uniformity across all nodes in our decentarlized system
    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We are only looking for chains longer that ours
        max_length = len(self.chain)

        # Checking for the length of each chain in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.validate_chain(chain):
                    new_chain = chain
                    max_length = length

        # Replace our chain with a new, longer, valid chain in our network (if present)
        if new_chain:
            self.chain = new_chain
            return True

        return False






# Making the blockchain interactive using HTTP requests
# Flask work starts here : 



# Instantaniate our Node
app = Flask(__name__)


# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')


# Instantaniate the Blockchain
blockchain = Blockchain()



@app.route('/mine', methods=['GET'])
def mine():
    # We run the Proof of Work of Algorithm to get next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']

    proof = blockchain.proof_of_work(last_proof)

    # Reward to miner for finding PoW
    # Here the sender is "0" to signnify that this node mined a new coin.
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    # Forge the new block by adding it to the new chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof,previous_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    
    values = request.get_json(force=True)

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # Create a new transaction
    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])

    response = {'message':f'Transaction will be added at block {index}'}
    return jsonify(response),201



@app.route('/chain', methods=['GET'])
def full_chain():
    response = { 
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response),200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json(force=True)

    nodes = values['nodes']
    if nodes is None:
        return "Error: Please Supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register(node)

    response = {
        'message': "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201



@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "Our chain was replaced",
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': "Our chain is authorative",
            'chain': blockchain.chain
        }

    return jsonify(response), 200




if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000)