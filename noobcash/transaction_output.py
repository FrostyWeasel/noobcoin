from Crypto.Hash import SHA256

class TransactionOutput:
    def __init__(self, recipient_public_key, value, parent_transaction_id) -> None:        
        # public key of recipient
        self.recipient = recipient_public_key
        
        # coupon amount
        self.value = value
        
        # parent id
        self.parent_transaction_id = parent_transaction_id
        
        self.id = self.hash_function().hexdigest()
        
    def hash_function(self):
        # Returns the hash-id of the transaction using sender, recipient, amount and inputs which create a unique hash
        my_hash = SHA256.new()
        my_hash.update(self.recipient.encode('utf-8'))
        my_hash.update(self.parent_transaction_id.encode('utf-8'))
        
        return my_hash
    
    def to_dict(self):
        return {
        'recipient': self.recipient,
        'value': self.value,
        'parent_transaction_id': self.parent_transaction_id,
        'id': self.id            
    }

    def __radd__(self, cum):
        return cum + self.value
        
    def is_mine(self, public_key):
        return self.recipient == public_key
 