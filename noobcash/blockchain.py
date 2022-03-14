

class Blockchain:
    def __init__(self):
        self.chain = []
        self.last_hash = None
        
    def is_transaction_input_valid(self, transaction_input):
        # 1. Find inputs parent transaction in blockchain
        # 2. Look at parent transactions outputs and verify that for a transaction output the data much given transaction input
        # 3. Make sure that this transaction input was not already spent on a different transaction