import base64
from Crypto.Hash import SHA256

class TransactionOutput:
    def __init__(self, recipient_public_key, value, parent_transaction_id, trans_id=None) -> None:        
        # public key of recipient
        self.recipient = recipient_public_key
        
        # coupon amount
        self.value = value
        
        # parent id
        self.parent_transaction_id = parent_transaction_id
        
        self.id = self.hash_function() if trans_id is None else trans_id
    
    @classmethod
    def from_dictionary(cls, dictionary):
        recipient = dictionary['recipient']
        value = dictionary['value']
        parent_transaction_id = base64.b64decode(dictionary['parent_transaction_id'])
        trans_id = base64.b64decode(dictionary['id'])
        
        return cls(recipient, value, parent_transaction_id, trans_id)
        
    def hash_function(self):
        # Returns the hash-id of the transaction using sender, recipient, amount and inputs which create a unique hash
        my_hash = SHA256.new()
        my_hash.update(self.recipient.encode('utf-8'))
        my_hash.update(self.parent_transaction_id)
        
        return my_hash.digest()
    
    def to_dict(self):
        return {
        'recipient': self.recipient,
        'value': self.value,
        'parent_transaction_id': base64.b64encode(self.parent_transaction_id).decode('utf-8'),
        'id': base64.b64encode(self.id).decode('utf-8')            
    }

    def __radd__(self, cum):
        return cum + self.value
        
    def is_mine(self, public_key):
        return self.recipient == public_key
 