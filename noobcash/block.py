
from datetime import datetime
import noobcash
from noobcash.transaction import Transaction
from Crypto.Hash import SHA256

class Block:
    def __init__(self, previous_hash):
        self.previous_hash = previous_hash
        self.timestamp = datetime.now()
        self.hash = None
        self.nonce = 0
        self.is_mining = False
        self.list_of_transactions: list[Transaction] = []
        self.capacity = noobcash.CAPACITY
    
    def compute_hash(self):
        my_hash = SHA256.new()
        my_hash.update(self.previous_hash)
        my_hash.update(self.timestamp)
        
        for transaction in self.list_of_transactions:
            my_hash.update(transaction.transaction_id)
            
        my_hash.update(bytes(self.nonce))
        
        return my_hash.digest().decode('utf-8')
    
    def get_transaction(self, transaction_id):
        for transaction in self.list_of_transactions:
            if transaction.transaction_id == transaction_id:
                return transaction
            
        return None
    
    def has_transaction(self, transaction_id):
        for transaction in self.list_of_transactions:
            if transaction.transaction_id == transaction_id:
                return True
            
        return False
    
    def start_mining(self):
        self.is_mining = True
        print('Diggy diggy')
        self.hash = self.compute_hash()
        print(f'my new hash: {self.hash}')

    def add_transaction(self, transaction: Transaction):
        # add a transaction to the block            
        self.list_of_transactions.append(transaction)
        
    def get_length(self):
        return len(self.list_of_transactions)