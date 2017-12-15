	######################################### 
	#										#
	# Implementation of Basic Blockchain	#
	#										#
	#########################################

import hashlib
import json
from time import time



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