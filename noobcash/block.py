
from datetime import datetime
import blockchain
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
    
    def compute_hash(self):
        my_hash = SHA256.new()
        my_hash.update(self.previous_hash)
        my_hash.update(self.timestamp)
        
        for transaction in self.list_of_transactions:
            my_hash.update(transaction.transaction_id)
            
        my_hash.update(bytes(self.nonce))
        
        return my_hash
    
    def get_transaction(self, transaction_id):
        for transaction in self.list_of_transactions:
            if transaction.transaction_id == transaction_id:
                return transaction
            
        return None

    def add_transaction(self, transaction: Transaction, blockchain: Blockchain):
        # add a transaction to the block
        # 1. make sure that transaction signature is valid
        # 2. check that all transaction inputs are in blockchain and are not already spent
        # 3. check all transactions in blockchain to make sure than the transaction has not already been spent
        # * Check that transaction is not already in blockchain
        is_not_in_blockchain = not blockchain.is_transaction_spent(transaction.transaction_id)
        
        # * Check that transaction is valid
        has_valid_signature = transaction.verify_signature()
        
        senders_public_key = transaction.sender_address
        
        # 1. Get parent transaction that generated current transactions input
        for transaction_input in transaction.transaction_inputs:
            blockchain.is_transaction_input_valid(transaction_input)

        