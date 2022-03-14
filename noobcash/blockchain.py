

from noobcash.block import Block


class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self.last_hash = None
        
    def is_transaction_spent(self, transaction_id):
        has_transaction = False
        for block in self.chain:
            has_transaction = block.has_transaction(transaction_id=transaction_id)
            if has_transaction is True:
                break
            
        return has_transaction