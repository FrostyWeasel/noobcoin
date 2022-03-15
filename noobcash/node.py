# import block
from noobcash import blockchain_api
from noobcash.blockchain import Blockchain
from noobcash.transaction import Transaction
from noobcash.wallet import Wallet
from noobcash.transaction_input import TransactionInput
from noobcash.block import Block
import requests

class Node:
    def __init__(self):
        # self.NBC=100
        
        self.id = None
        #TODO: Actually initialize during bootstrap creation and node registration
        self.chain: Blockchain = Blockchain()
        #self.current_id_count
        #self.NBCs
        self.wallet = self.create_wallet()
        
        self.current_block = None
        self.active_blocks: list[Block] = []
        
        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance 
        self.ring = [{'ip': '127.0.0.1', 'port': '5000'}]   


    # def create_new_block(self):
    #     5

    def create_wallet(self) -> Wallet:
        # Create a wallet for this node, with a public key and a private key
        return Wallet()
    
    def update_current_block(self):
        if self.current_block is not None:
            return
        
        # TODO: Actually update the freaking blockchain
        # self.update_blockchain()
        print('Blockchain successfully updated')
        
        new_block = Block(self.chain.last_hash)
        self.active_blocks.append(new_block)
        self.current_block = new_block

    # def register_node_to_ring(self):
    #     # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    #     # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    #     5


    def create_transaction(self, receiver_public_key, amount):
        # Create a transaction with someone giving them the requested amount
        public_key, private_key = self.wallet.get_key_pair()
        my_UTXOs = self.wallet.UTXOs
        
        transaction_inputs = [TransactionInput(UTXO) for UTXO in my_UTXOs]
        
        # Try creating it and handle the error of not having enough balance
        try:
            new_transaction = Transaction(public_key.decode(), receiver_public_key.decode(), amount=amount, transaction_inputs=transaction_inputs)
        except Exception as e:
            print(e)
            raise e
        
        # Sign the transaction
        new_transaction.sign_transaction(private_key)
        
        # Create the corresponding UTXOs
        transaction_outputs = new_transaction.transaction_outputs
        
        self.wallet.UTXOs = []
        for transaction_output in transaction_outputs:
            # Add the change to my wallet as a UTXO
            if transaction_output.is_mine(public_key):
                self.wallet.add_transaction_output(transaction_output)

        #update_ring(transaction_outputs)
        return new_transaction
    
    def update_blockchain(self):
        chains = []
        for key in self.ring.keys():
            node_id = self.ring[key]['id']
            node_ip = self.ring[key]['ip']
            node_port = self.ring[key]['port']
            
            if node_id != self.id:
                chain = blockchain_api.get_blockchain_from_node(node_ip, node_port)
                chains.append(chain)
                
        self.chain = self.consensus(chains)
        
    def consensus(self, chains):
        biggest = -1
        winner = None
        for chain in chains:
            chain_length = chain.get_length()
            if chain_length > biggest:
                biggest = chain_length
                winner = chain
                
        return winner

    # def update_ring(transaction_outputs):
    #     for transaction_output in transaction_outputs:
    #         self.ring.

    # def broadcast_transaction(self, transaction):
    #     5



    def validate_transaction(self, transaction: Transaction, current_block: Block):
        # 1. make sure that transaction signature is valid
        # 2. check that the sender node has enough balance based on its UTXOs
        # * Check that transaction is not already in blockchain
        is_not_in_blockchain = not self.chain.is_transaction_spent(transaction.transaction_id)
        
        is_not_in_block = not current_block.has_transaction(transaction.transaction_id)
        
        # * Check that transaction is valid
        has_valid_signature = transaction.verify_signature()
        
        sender_address = transaction.sender_address
        
        has_invalid_transaction_inputs = False
        for transaction_input in transaction.transaction_inputs:
            is_unspent_transaction = False
            
            is_unspent_transaction = transaction_input.id in self.ring[sender_address]['UTXOs']
            
            if is_unspent_transaction is False:
                has_invalid_transaction_inputs = True
                break
        
        is_valid_transaction = is_not_in_blockchain and is_not_in_block and has_valid_signature and not has_invalid_transaction_inputs
        
        return is_valid_transaction

    def add_transaction_to_block(self, transaction: Transaction):
        self.update_current_block()
        is_valid = self.validate_transaction(transaction, self.current_block)
        
        if is_valid is True:
            sender_transaction_outputs = transaction.get_sender_transaction_output()
            recipient_transaction_outputs = transaction.get_recipient_transaction_output()
            sender_address = transaction.sender_address
            recipient_address = transaction.recipient_address
            
            for transaction_input in transaction.transaction_inputs:
                del self.ring[sender_address]['UTXOs'][transaction_input.id]
            
            self.ring[sender_address]['UTXOs'][sender_transaction_outputs.id] = sender_transaction_outputs
            self.ring[recipient_address]['UTXOs'][recipient_transaction_outputs.id] = recipient_transaction_outputs
            
            self.current_block.add_transaction(transaction)
            
            if self.current_block.capacity == self.current_block.get_length():
                self.mine_block(self.current_block)
            


    def mine_block(self, current_block):
        self.current_block.start_mining()
        self.current_block = None

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

