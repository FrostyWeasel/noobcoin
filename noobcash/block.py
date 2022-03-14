
from datetime import datetime
import blockchain
import noobcash
from noobcash.transaction import Transaction
from noobcash.blockchain import Blockchain
from Crypto.Hash import SHA256

class Block:
    def __init__(self, previous_hash):
        self.previous_hash = previous_hash
        self.timestamp = datetime.now()
        self.hash = None
        self.nonce = 0
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
        print('Diggy diggy')
        self.hash = self.compute_hash()
        print(f'my new hash: {self.hash}')
    
    def validate_transaction(self, transaction: Transaction, blockchain: Blockchain):
        # 1. make sure that transaction signature is valid
        # 2. check that the sender node has enough balance based on its UTXOs
        # * Check that transaction is not already in blockchain
        is_not_in_blockchain = not blockchain.is_transaction_spent(transaction.transaction_id)
        
        # * Check that transaction is valid
        has_valid_signature = transaction.verify_signature()
        
        sender_address = transaction.sender_address
        
        has_invalid_transaction_inputs = False
        for transaction_input in transaction.transaction_inputs:
            is_unspent_transaction = False
            
            is_unspent_transaction = transaction_input.id in noobcash.current_node.ring[sender_address]['UTXOs']
            
            if is_unspent_transaction is False:
                has_invalid_transaction_inputs = True
                break
        
        is_valid_transaction = is_not_in_blockchain and has_valid_signature and not has_invalid_transaction_inputs
        
        return is_valid_transaction

    def add_transaction(self, transaction: Transaction, blockchain: Blockchain):
        # add a transaction to the block
        is_valid_transaction = self.validate_transaction(transaction, blockchain)
        
        if is_valid_transaction is True:
            sender_transaction_outputs = transaction.get_sender_transaction_output()
            recipient_transaction_outputs = transaction.get_recipient_transaction_output()
            sender_address = transaction.sender_address
            recipient_address = transaction.recipient_address
            
            for transaction_input in transaction.transaction_inputs:
                del noobcash.current_node.ring[sender_address]['UTXOs'][transaction_input.id]
            
            noobcash.current_node.ring[sender_address]['UTXOs'][sender_transaction_outputs.id] = sender_transaction_outputs
            noobcash.current_node.ring[recipient_address]['UTXOs'][recipient_transaction_outputs.id] = recipient_transaction_outputs
            
            self.list_of_transactions.append(transaction)
            
            if self.list_of_transactions == self.capacity:
                self.start_mining()
        else:
            print('Bad boy sent me invalid transaction')
            