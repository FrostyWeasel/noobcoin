# import block
from  . import transaction
from . import wallet
from . import transaction_input

class Node:
    def __init__(self):
        self.NBC=100;
        ##set
        
        
        self.id = None
        #self.chain
        #self.current_id_count
        #self.NBCs
        self.wallet = self.create_wallet()
        
        #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
        self.ring = [{'ip': '127.0.0.1', 'port': '5000'}]   


    # def create_new_block(self):
    #     5

    def create_wallet(self) -> wallet.Wallet:
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet()


    # def register_node_to_ring(self):
    #     #add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    #     #bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    #     5


    def create_transaction(self, receiver_public_key, amount):
        public_key, private_key = self.wallet.get_key_pair()
        my_UTXOs = self.wallet.UTXOs
        
        transaction_inputs = [transaction_input.TransactionInput(UTXO) for UTXO in my_UTXOs]
        
        try:
            new_transaction = transaction.Transaction(public_key.decode(), receiver_public_key.decode(), amount=amount, transaction_inputs=transaction_inputs)
        except Exception as e:
            print(e)
            raise e
        
        new_transaction.sign_transaction(private_key)
        
        transaction_outputs = new_transaction.transaction_outputs
        
        self.wallet.UTXOs = []
        for transaction_output in transaction_outputs:
            if(transaction_output.is_mine(public_key)):
                self.wallet.add_transaction_output(transaction_output)
                
        return new_transaction

    # def broadcast_transaction(self):
    #     5



    # def validdate_transaction(self):
    #     #use of signature and NBCs balance
    #     5


    # def add_transaction_to_block(self):
    #     #if enough transactions  mine
    #     5



    # def mine_block(self):
    #     5



    # def broadcast_block(self):
    #     5


        

    # def valid_proof(self, difficulty=MINING_DIFFICULTY):
    #     5




    # #consensus functions

    # def valid_chain(self, chain):
    #     #check for the longer chain accroose all nodes
    #     5


    # def resolve_conflicts(self):
    #     #resolve correct chain
    #     5

