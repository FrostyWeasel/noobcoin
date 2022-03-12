from . import transaction_output

class TransactionInput:
    def __init__(self, transaction_output: transaction_output.TransactionOutput) -> None:
        # public key of recipient
        self.recipient= transaction_output.recipient
        
        # coupon amount
        self.value = transaction_output.value
        
        # parent id
        self.parent_transaction_id = transaction_output.parent_transaction_id

    def __radd__(self, cum):
        return cum + self.value
        
    def is_mine(self, public_key):
        return self.recipient == public_key
