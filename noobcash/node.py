# import block
import base64
import copy
import threading
from dataclasses import dataclass

import Crypto
import requests
from Crypto.Hash import SHA256

import noobcash
from noobcash import block
from noobcash.api import blockchain_api, block_api
from noobcash.block import Block
from noobcash.blockchain import Blockchain
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput
from noobcash.wallet import Wallet


class Node:
    def __init__(self):
        # self.NBC=100
        
        self.id = None
        self.chain: Blockchain = Blockchain()
        #self.current_id_count
        #self.NBCs
        self.wallet = self.create_wallet()
        
        # Transaction ids so that we don't double check a transaction
        self.processed_transactions = set()
        
        self.current_block = None
        self.active_blocks: list[Block] = []
        
        
        # TODO: Add to this whenever you add a block to the blockchain
        # * This holds the state of all blocks in the blockchain
        self.shadow_log = {'block_hash': {'ring': , 'processed_transactions':, 'wallet_utxos'}}
        # self.current_block_log = {'ring': , 'processed_transactions':, 'wallet_utxos'}
        
        # Here we store information for every node, as its id, its address (ip:port) its public key and its balance 
        self.ring = { '0': { 'ip': '127.0.0.1', 'port': '5000' } }   

    # def create_new_block(self):
    #     5

    def create_wallet(self):
        # Create a wallet for this node, with a public key and a private key
        return Wallet()
    
    def create_initial_blockchain(self):
        genesis_transaction_input = TransactionInput(TransactionOutput(self.wallet.public_key.decode(), 100*noobcash.NODE_NUM, base64.b64encode(SHA256.new(b'parent_id').digest()).decode('utf-8')))
        genesis_transaction = Transaction(Crypto.PublicKey.RSA.generate(2048).public_key().export_key().decode(), self.wallet.public_key.decode("utf-8"), 100*noobcash.NODE_NUM, [genesis_transaction_input])
        
        genesis_transaction_output = genesis_transaction.get_recipient_transaction_output()
        
        genesis_block = Block(base64.b64encode(SHA256.new(bytes(1)).digest()).decode('utf-8'))

        genesis_block.add_transaction(genesis_transaction)
        self.processed_transactions.add(genesis_transaction.transaction_id)
        genesis_block.hash = base64.b64encode(genesis_block.compute_hash()).decode('utf-8')
        
        self.current_block = genesis_block
                
        self.wallet.UTXOs = []
        self.wallet.add_transaction_output(genesis_transaction_output)
        self.id = '0'
        self.ring[self.id]['id'] = self.id
        self.ring[self.id]['UTXOs'] = { genesis_transaction_output.id: genesis_transaction_output }
        self.ring[self.id]['public_key'] = self.wallet.public_key.decode()
        
        self.chain = Blockchain()
        self.chain.add_block(genesis_block)
        
    def handle_genesis_block(self, genesis_block: Block):
        self.chain.add_block(genesis_block)
        
    def update_current_block(self):
        if self.current_block is not None:
            return
        
        # * This happens so that we has the most recent last block to get the hash from
        # * but in our scenario this is not really necessary because all nodes actually update their chains almost at the same time
        self.consensus()
        
        new_block = Block(self.chain.last_hash)
        self.active_blocks.append(new_block)
        self.current_block = new_block
        
    def validate_block(self, block: Block, previous_block: Block):
        # TODO: Use the state from the last block in the blockchain before this one
        
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
        # TODO: Use state from last block on which we agree with the node that sent us the part of their blockchain
        
        processed_transactions_backup = copy.deepcopy(self.processed_transactions)
        ring_backup = copy.deepcopy(self.ring)
        wallet_utxos_backup = copy.deepcopy(self.wallet.UTXOs)
        
        # Reset state to before any transaction occurred
        self.processed_transactions = set()
        for key in self.ring.keys():
            self.ring[key]['UTXOs'] = {}
        self.wallet.UTXOs = []
        
        # Check that genesis block is the same with mine(which i know is the correct one because i am a good boy and i follow the protocol) and then process its transactions
        genesis_block = chain.chain[0]
        is_genesis_block_valid = self.chain.chain[0] == genesis_block
        
        if is_genesis_block_valid:
            genesis_transaction = genesis_block.list_of_transactions[0]
            # Process genesis transaction (this requires special processing because there is no sender)
            recipient_address = genesis_transaction.recipient_address
            
            recipient_node_id = self.get_node_id_from_address(recipient_address)
            
            recipient_transaction_output = genesis_transaction.get_recipient_transaction_output()
            
            if recipient_address == self.wallet.public_key.decode():
                self.wallet.add_transaction_output(recipient_transaction_output)
            
            self.ring[recipient_node_id]['UTXOs'][recipient_transaction_output.id] = recipient_transaction_output
            
            self.processed_transactions.add(genesis_transaction.transaction_id)
            
            has_invalid_block = False
            for block, previous_block in zip(chain.chain[1:], chain.chain[:-1]):
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
        
            return True, {'ring': ring, 'processed_transactions': processed, 'wallet_utxos': wallet_utxos}
        else:
            return False, None

    def add_block_to_blockchain(self, block: Block):
        # TODO: Update shadow log
        is_valid_block = self.validate_block(block, self.chain.chain[-1])
        is_next_block = self.chain.last_hash == block.hash
        
        if is_valid_block:
            if not is_next_block:
                self.consensus()
                return False
            else:
                self.chain.add_block(block)
                return True
                
    def consensus(self):
        # TODO: Only receive the delta blocks
        chains = []
        for key in self.ring.keys():
            node_id = key
            node_ip = self.ring[key]['ip']
            node_port = self.ring[key]['port']
            
            if node_id != self.id:
                chain = blockchain_api.get_blockchain_from_node(node_ip, node_port)
                is_valid, data = self.validate_blockchain(chain)
                if is_valid:
                    chains.append({ 'chain': chain, 'ring': data['ring'], 'processed_transactions': data['processed_transactions'], 'wallet_utxos': data['wallet_utxos'] })
            else:
                chains.append({ 'chain': self.chain,  'ring': self.ring, 'processed_transactions': self.processed_transactions, 'wallet_utxos': self.wallet.UTXOs })
                
        winner_chain = self.get_longest_chain(chains)
        
        self.chain = winner_chain['chain']
        self.ring = winner_chain['ring']
        self.processed_transactions = winner_chain['processed_transactions']
        self.wallet.UTXOs = winner_chain['wallet_utxos']
        
        
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
        
        # * This runs before we add the new transaction to a block
        # self.process_transaction(new_transaction)
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
        if sender_address == self.wallet.public_key.decode():
            self.wallet.add_transaction_output(sender_transaction_output)

        # ! This only works because nodes following this code use all their UTXOs as trans inputs when creating a transaction
        self.ring[sender_node_id]['UTXOs'] = {}
        # for transaction_input in transaction.transaction_inputs:
        #     del self.ring[sender_node_id]['UTXOs'][transaction_input.id]
        
        self.ring[sender_node_id]['UTXOs'][sender_transaction_output.id] = sender_transaction_output
        self.ring[recipient_node_id]['UTXOs'][recipient_transaction_output.id] = recipient_transaction_output
        
        self.processed_transactions.add(transaction.transaction_id)

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
        # This creates a new block if one is not already active
        self.update_current_block()
        
        is_valid = self.validate_transaction(transaction)
        is_not_in_block = not self.current_block.has_transaction(transaction.transaction_id)
        
        # print(f'[add_transaction_to_block] Transaction validity: {is_valid}, not in current block {is_not_in_block}')
        
        was_already_processed = transaction.transaction_id in self.processed_transactions
        
        if is_valid and is_not_in_block and not was_already_processed:
            self.process_transaction(transaction)
            
            self.current_block.add_transaction(transaction)
            
            if self.current_block.capacity == self.current_block.get_length():
                self.mine_block()
            
            # print(f'[add_transaction_to_block] Wallet after adding transaction: {self.wallet.balance()}')
            # print(f'[add_transaction_to_block] Block after adding transaction: {self.current_block.to_dict()}')

    def threaded_mining(self, callback_function):
        lock_mining.acquire()
        
        # * Only set current block to none when i actually start mining
        # * this prevents weird behavior such as the current block being set to none by another thread
        self.current_block = None
        
        mined_block = self.current_block.mine()
        
        callback_function(mined_block)
        
    def mining_end(self, mined_block: Block):
        # Check that mining was successful
        has_valid_hash = mined_block.validate_hash()
        
        is_next_in_chain = self.chain.last_hash == mined_block.hash
        
        if has_valid_hash and is_next_in_chain:
            self.chain.add_block(mined_block)
            
            # Broadcast block
            block_api.broadcast_block(mined_block)
            
        # * This updates the hash of the current block before potentially allowing it to enter the mining phase
        if self.current_block is not None:
            # TODO: Could this cause a problem because we change data that is also used by another thread?
            self.current_block.previous_hash = self.chain.last_hash
        
        lock_mining.release()
            
    def mine_block(self):
        # TODO: This should be running on another thread
        
        # TODO: This stores the state(a state consists of all the data structures that change during transaction processing)
        # TODO: before we start mining because it is the final state of the block
        # TODO: which should be added to our shadow_log if this block ends up in the blockchain
        # * This holds the states of our currently mining blocks
        self.active_blocks_log = {self.current_block.timestamp: self.ring, self.processed, self.}
        
        
        mining_thread = threading.Thread(target=self.threaded_mining, args=(self.mining_end))
        mining_thread.start()
        
        # TODO: Discover when we returned from the mining thread check that the minning was successful(hash meets difficulty and previous hash is correct) if it was then broadcast block and remove from active blocks
        
        
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

