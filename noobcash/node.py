# import block
from noobcash import blockchain_api
from noobcash.blockchain import Blockchain
from noobcash.transaction import Transaction
from noobcash.wallet import Wallet
from noobcash.transaction_input import TransactionInput
from noobcash.block import Block
import requests
import threading
import copy

class Node:
    def __init__(self):
        # self.NBC=100
        
        self.id = None
        #TODO: Actually initialize during bootstrap creation and node registration
        self.chain: Blockchain = Blockchain()
        #self.current_id_count
        #self.NBCs
        self.wallet = self.create_wallet()
        
        self.processed_transactions = set()
        
        self.current_block = None
        self.active_blocks: list[Block] = []
        
        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance 
        self.ring = { '0': { 'ip': '127.0.0.1', 'port': '5000' } }   

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
        

    def validate_block(self, block: Block, previous_block: Block):
        processed_transactions_backup = copy.deepcopy(self.processed_transactions)
        ring_backup = copy.deepcopy(self.ring)
        wallet_utxos_backup = copy.deepcopy(self.wallet.UTXOs)
        
        is_next_block = previous_block.hash == block.hash
        
        has_invalid_transaction = False
        for transaction in block.list_of_transactions:
            if self.validate_transaction(transaction) is False:
                has_invalid_transaction = True
                break
            else:
                was_already_processed = transaction.id in self.processed_transactions
                if not was_already_processed:
                    self.process_transaction(transaction)
            
        has_valid_hash = block.validate_hash()
        
        if not has_valid_hash or has_invalid_transaction or not is_next_block:
            # Reverse results of transaction processing
            self.wallet.UTXOs = wallet_utxos_backup
            self.ring = ring_backup
            self.processed_transactions = processed_transactions_backup
        
        return has_valid_hash and not has_invalid_transaction

    def validate_blockchain(self, chain: Blockchain):
        processed_transactions_backup = copy.deepcopy(self.processed_transactions)
        ring_backup = copy.deepcopy(self.ring)
        wallet_utxos_backup = copy.deepcopy(self.wallet.UTXOs)
        
        # Reset state to before any transaction occurred
        self.processed_transaction = set()
        for key in self.ring.keys():
            self.ring[key]['UTXOs'] = {}
        self.wallet.UTXOs = []
        
        # Check that genesis block is the same with mine(which i know is the correct one because i am a good boy and i follow the protocol) and then process its transactions
        genesis_block = chain.chain[0]
        is_genesis_block_valid = self.chain.chain[0] == genesis_block
        
        if is_genesis_block_valid:
            genesis_transaction = genesis_block.list_of_transactions[0]
            self.process_transaction(genesis_transaction)
            
            has_invalid_block = False
            for block, previous_block in zip(chain[1:], chain[:-1]):
                is_block_valid = self.validate_block(block, previous_block)
                if is_block_valid:
                    has_invalid_block = True
                    break
            
            if has_invalid_block:
                return False, None
            
            ring = copy.deepcopy(self.ring)
            processed = copy.deepcopy(self.processed_transactions)
            wallet_utxos = copy.deepcopy(self.wallet.UTXOs)
            
            self.ring = ring_backup
            self.processed_transactions = processed_transactions_backup
            self.wallet.UTXOs = wallet_utxos_backup 
        
            return True, (ring, processed, wallet_utxos)
        else:
            return False, None

    def add_block_to_blockchain(self, block: Block):
        is_valid_block = self.validate_block(block)
        is_next_block = self.chain.last_hash == block.hash

        if is_valid_block:
            if not is_next_block:
                self.consensus()
                
    def consensus(self):
        chains = []
        for key in self.ring.keys():
            node_id = key
            node_ip = self.ring[key]['ip']
            node_port = self.ring[key]['port']
            
            if node_id != self.id:
                chain, node_ring, node_processed_transactions = blockchain_api.get_blockchain_from_node(node_ip, node_port)
                is_valid = self.validate_blockchain(chain, node_ring, node_processed_transactions)
                if is_valid:
                    chains.append({ 'chain': chain, 'node_ring': node_ring, 'node_processed_transactions': node_processed_transactions })
            else:
                chains.append({ 'chain': self.chain, 'node_ring': self.ring, 'node_processed_transactions': self.processed_transactions })
                
        winner_chain = self.get_longest_chain(chains)
        
        self.chain = winner_chain['chain']
        # TODO: Possibly contact winner node to get data from
        
    def get_longest_chain(self, chains):
        biggest = -1
        
        winner = None
        
        for chain in chains:
            chain_length = chain['chain'].get_length()
            if chain_length > biggest:
                biggest = chain_length
                winner = chain
                
        return winner

    def create_transaction(self, node_id, amount):
        # Create a transaction with someone giving them the requested amount
        receiver_public_key = self.ring[node_id]['public_key']
        
        public_key, private_key = self.wallet.get_key_pair()
        my_UTXOs = self.wallet.UTXOs
        
        transaction_inputs = [TransactionInput(UTXO) for UTXO in my_UTXOs]
        
        # Try creating it and handle the error of not having enough balance
        try:
            new_transaction = Transaction(public_key.decode(), receiver_public_key, amount=amount, transaction_inputs=transaction_inputs)
        except Exception as e:
            print(e)
            raise e
        
        # Sign the transaction
        new_transaction.sign_transaction(private_key)
        
        # # Create the corresponding UTXOs
        # transaction_outputs = new_transaction.transaction_outputs
        
        self.wallet.UTXOs = []
        self.process_transaction(new_transaction)
        # for transaction_output in transaction_outputs:
        #     # Add the change to my wallet as a UTXO
        #     if transaction_output.is_mine(public_key):
        #         self.wallet.add_transaction_output(transaction_output)
        #     else:
        #         self.ring[node_id]['UTXOs'][transaction_output.id] = transaction_output
                
        return new_transaction
    
    # def update_blockchain(self):
    #     chains = []
    #     for key in self.ring.keys():
    #         node_id = key
    #         node_ip = self.ring[key]['ip']
    #         node_port = self.ring[key]['port']
            
    #         if node_id != self.id:
    #             chain = blockchain_api.get_blockchain_from_node(node_ip, node_port)
    #             chains.append(chain)
                
    #     self.chain = self.consensus(chains)
        
    # def consensus(self, chains):
    #     biggest = -1
    #     winner = None
    #     for chain in chains:
    #         chain_length = chain.get_length()
    #         if chain_length > biggest:
    #             biggest = chain_length
    #             winner = chain
                
    #     return winner

    # def update_ring(transaction_outputs):
    #     for transaction_output in transaction_outputs:
    #         self.ring.

    # def broadcast_transaction(self, transaction):
    #     5

    def process_transaction(self, transaction: Transaction):
        sender_address = transaction.sender_address
        recipient_address = transaction.recipient_address
        
        sender_node_id = self.get_node_id_from_address(sender_address)
        recipient_node_id = self.get_node_id_from_address(recipient_address)
        
        sender_transaction_output = transaction.get_sender_transaction_output()
        recipient_transaction_output = transaction.get_recipient_transaction_output()
        
        if recipient_address == self.wallet.public_key.decode():
            self.wallet.add_transaction_output(recipient_transaction_output)

        # ! This only works because nodes following this code use all their UTXOs as trans inputs when creating a transaction
        self.ring[sender_node_id]['UTXOs'] = {}
        # for transaction_input in transaction.transaction_inputs:
        #     del self.ring[sender_node_id]['UTXOs'][transaction_input.id]
        
        self.ring[sender_node_id]['UTXOs'][sender_transaction_output.id] = sender_transaction_output
        self.ring[recipient_node_id]['UTXOs'][recipient_transaction_output.id] = recipient_transaction_output
        
        self.processed_transactions.add(transaction.id)

    def validate_transaction(self, transaction: Transaction):
        # 1. make sure that transaction signature is valid
        # 2. check that the sender node has enough balance based on its UTXOs
        # * Check that transaction is not already in blockchain
        is_not_in_blockchain = not self.chain.is_transaction_spent(transaction.transaction_id)
        
        # * Check that transaction is valid
        has_valid_signature = transaction.verify_signature()
        
        sender_address = transaction.sender_address
        
        sender_node_id = self.get_node_id_from_address(sender_address)
        
        has_invalid_transaction_inputs = False
        for transaction_input in transaction.transaction_inputs:
            is_unspent_transaction = False
            
            is_unspent_transaction = transaction_input.id in self.ring[sender_node_id]['UTXOs']
            
            if is_unspent_transaction is False:
                has_invalid_transaction_inputs = True
                break
        
        is_valid_transaction = is_not_in_blockchain and has_valid_signature and not has_invalid_transaction_inputs
        
        return is_valid_transaction

    def add_transaction_to_block(self, transaction: Transaction):
        self.update_current_block()
        
        is_valid = self.validate_transaction(transaction)
        is_not_in_block = not self.current_block.has_transaction(transaction.transaction_id)
        
        print(f'[add_transaction_to_block] Transaction validity: {is_valid}, not in current block {is_not_in_block}')
        
        was_already_processed = transaction.id in self.processed_transactions
        
        if is_valid and is_not_in_block and not was_already_processed:
            self.process_transaction(transaction)
            
            self.current_block.add_transaction(transaction)
            
            if self.current_block.capacity == self.current_block.get_length():
                self.mine_block(self.current_block)
            
            print(f'[add_transaction_to_block] Wallet after adding transaction: {self.wallet.balance()}')
            print(f'[add_transaction_to_block] Block after adding transaction: {self.current_block}')

    def mine_block(self, current_block):
        self.current_block.mine()
        self.current_block = None
        
    def get_node_id_from_address(self, address):
        node_id = None
        for key, node_info in self.ring.items():
            if node_info['public_key'] == address:
                node_id = key
                break
        return node_id

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

