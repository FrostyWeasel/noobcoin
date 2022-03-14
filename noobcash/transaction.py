from collections import OrderedDict

import binascii
import uuid

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

# import requests
# from flask import Flask, jsonify, request, render_template

class Transaction:

    def __init__(self, sender_address, recipient_address, amount, transaction_inputs):
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        #self.recipient_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        #self.amount: το ποσό που θα μεταφερθεί
        #self.transaction_id: το hash του transaction
        #self.transaction_inputs: λίστα από Transaction Input 
        #self.transaction_outputs: λίστα από Transaction Output 
        #selfSignature
        
        # Basic info: Who sends to whom and how much money (addresses are public keys)
        self.sender_address: str = sender_address
        self.recipient_address: str = recipient_address
        self.amount = amount
        
        self.transaction_inputs: list[TransactionInput] = transaction_inputs
        
        self.transaction_id = self.hash_function().hexdigest()
        
        have_enough_balance = self.check_balance()
        
        if not have_enough_balance:
            raise Exception('Not enough balance to perform transaction')
        
        self.transaction_outputs = self.compute_outputs()
        
        
    def compute_outputs(self):
        # Create the UTXOs of the transaction to be sent to the two parties
        change = sum(self.transaction_inputs) - self.amount
        change_output = TransactionOutput(self.sender_address, change, self.transaction_id)
        
        recipient_output = TransactionOutput(self.recipient_address, self.amount, self.transaction_id)
        
        return [change_output, recipient_output]
    
    def get_sender_transaction_output(self):
        return self.transaction_outputs[0]
        
    def get_recipient_transaction_output(self):
        return self.transaction_outputs[1]
        
    def check_balance(self):
        # Returns true if the sender's wallet has enough money to conduct the transaction
        total_balance = sum(self.transaction_inputs)
        
        return total_balance >= self.amount


    def hash_function(self):
        # Returns the hash-id of the transaction using sender, recipient, amount and inputs which create a unique hash
        my_hash = SHA256.new()
        my_hash.update(self.sender_address.encode('utf-8'))
        my_hash.update(self.recipient_address.encode('utf-8'))
        
        my_hash.update(str(uuid.uuid4()).encode('utf-8'))

        for transaction_input in self.transaction_inputs:
            my_hash.update(transaction_input.recipient.encode('utf-8'))
            my_hash.update(transaction_input.parent_transaction_id.encode('utf-8'))
        
        return my_hash

    def to_dict(self):
        return {
            'sender_address': self.sender_address,
            'recipient_address': self.recipient_address,
            'amount': self.amount,
            'transaction_inputs': [transaction_input.to_dict() for transaction_input in self.transaction_inputs],
            'transaction_id': self.transaction_id,
            'transaction_outputs': [transaction_outputs.to_dict() for transaction_outputs in self.transaction_outputs]
        }
        

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        self.signature = PKCS1_v1_5.new(RSA.import_key(private_key)).sign(SHA256.new(self.transaction_id))
        
    def verify_signature(self):
        # 1) Check if data is still unchanged by re-hashing the data and comparing with the existing hash
        # 2) Check that the sender is really the one who sent me the transaction
        check_1 = self.transaction_id.digest() == self.hash_function().digest()
        check_2 = PKCS1_v1_5.new(RSA.import_key(self.sender_address)).verify(SHA256.new(self.transaction_id), self.signature)
        return check_1 and check_2

