import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

class Wallet:
    def __init__(self):
        # Generate a key pair and create an empty UTXO list (wallet hasn't participated in any transactions)
        keys = Crypto.PublicKey.RSA.generate(2048)
        
        self.public_key = keys.public_key().export_key()
        self.private_key = keys.export_key()
        self.UTXOs = []

    def balance(self):
        # Return the balance of the wallet
        # Works because UTXOs list contains transaction outputs with __radd__ method
        return sum(self.UTXOs)

    def add_transaction_output(self, transaction_output):
        # Will be called twice whenever a transaction is comitted to update the UTXOs of both wallets
        self.UTXOs.append(transaction_output)

    def get_key_pair(self):
        return (self.public_key, self.private_key)
        