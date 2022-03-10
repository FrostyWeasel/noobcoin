from venv import create
import block
from transaction import Transaction
import wallet

class node:
    def __init__(self):
        self.NBC=100;
        ##set

        #self.chain
        #self.current_id_count
        #self.NBCs
        self.wallet = self.create_wallet()

        #slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


    def create_new_block(self):
        5

    def create_wallet(self):
        #create a wallet for this node, with a public key and a private key
        return wallet.Wallet()


    def register_node_to_ring(self):
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        #bottstrap node informs all other nodes and gives the request node an id and 100 NBCs


    def create_transaction(self, receiver_public_key):
        #remember to broadcast it
        public_key, private_key = self.wallet.get_key_pair()
        transaction = Transaction(public_key, receiver_public_key, 20)
        transaction.sign_transaction(private_key)


    def broadcast_transaction(self):



    def validdate_transaction(self):
        #use of signature and NBCs balance


    def add_transaction_to_block(self):
        #if enough transactions  mine



    def mine_block(self):



    def broadcast_block(self):


        

    def valid_proof(self, difficulty=MINING_DIFFICULTY):




    #consensus functions

    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes


    def resolve_conflicts(self):
        #resolve correct chain

