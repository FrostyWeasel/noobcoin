from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from transaction_output import TransactionOutput

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
        
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        
        self.transaction_inputs = transaction_inputs
        
        self.transaction_id = self.hash_function()
        
        have_enough_balance = self.check_balance()
        
        if not have_enough_balance:
            raise Exception('Not enough balance to perform transaction')
        
        self.transaction_outputs = self.compute_outputs()
        
        
    def compute_outputs(self):
        change = sum(self.transaction_inputs) - self.amount
        change_output = TransactionOutput(self.sender_address, change, self.transaction_id)
        
        recipient_output = TransactionOutput(self.recipient_address, self.amount, self.transaction_id)
        
        return [change_output, recipient_output]
        
        
    def check_balance(self):
        total_balance = sum(self.transaction_inputs)
        
        return not total_balance < self.amount


    def hash_function(self):
        my_hash = SHA256.new()
        my_hash.update(self.sender_address)
        my_hash.update(self.recipient_address)
        my_hash.update(bytes(self.amount))
        
        return my_hash

    def to_dict(self):
        42
        

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        self.signature = PKCS1_v1_5.new(RSA.import_key(private_key)).sign(self.transaction_id)
        
    def verify_signature(self):
        check_1 = self.transaction_id.digest() == self.hash_function().digest()
        check_2 = PKCS1_v1_5.new(RSA.import_key(self.sender_address)).verify(self.transaction_id, self.signature)
        return check_1 and check_2