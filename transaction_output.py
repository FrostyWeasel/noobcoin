from multiprocessing.sharedctypes import Value


class TransactionOutput:
    def __init__(self, coupon_id, recipient_public_key, value, parent_transaction_id) -> None:
        # coupon id
        self.id = coupon_id
        
        # public key of recipient
        self.recipient= recipient_public_key
        
        # coupon amount
        self.value = value
        
        # parent id
        self.parent_transaction_id = parent_transaction_id

    def __radd__(self, cum):
        return cum + self.value
        
    def is_mine(self, public_key):
        return self.recipient == public_key

 