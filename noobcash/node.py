# import block
import base64
from copy import deepcopy
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
from noobcash.state import State

class Node:
    def __init__(self):
        
        self.id = None
        self.blockchain: Blockchain = Blockchain()
        self.wallet = Wallet()
        
        # Here we store non changing information for every node, as its id, its address (ip:port) its public key 
        self.ring = { '0': { 'ip': '127.0.0.1', 'port': '5000' } }

        self.current_block = None
        self.active_blocks: list[Block] = []
        
        # * This holds the state of all blocks in the blockchain
        self.shadow_log: dict[str, State] = {}
        
        # * This holds the state of all the blocks currently being processed
        # * This can be: 1. The block i am currently adding transactions to, 2. The block being mined, 3. A block i received from someone else and i am currently verifying it
        self.active_blocks_log: dict[str, State] = {}
        
        self.current_state: State | None = None

        self.mining_lock = threading.Lock()
        self.mining_sem = threading.Semaphore(value=2)

    def create_initial_blockchain(self):
        genesis_transaction_input = TransactionInput(TransactionOutput(self.wallet.public_key.decode(), 100*noobcash.NODE_NUM, base64.b64encode(SHA256.new(b'parent_id').digest()).decode('utf-8')))
        genesis_transaction = Transaction(Crypto.PublicKey.RSA.generate(2048).public_key().export_key().decode(), self.wallet.public_key.decode("utf-8"), 100*noobcash.NODE_NUM, [genesis_transaction_input])
        genesis_transaction_output = genesis_transaction.get_recipient_transaction_output()
        
        genesis_block = Block(base64.b64encode(SHA256.new(bytes(1)).digest()).decode('utf-8'))
        genesis_block.add_transaction(genesis_transaction)
        
        genesis_block.hash = base64.b64encode(genesis_block.compute_hash()).decode('utf-8')
                        
        self.wallet.UTXOs = []
        self.wallet.add_transaction_output(genesis_transaction_output)
        
        self.id = '0'
        
        self.ring[self.id]['public_key'] = self.wallet.public_key.decode()
        
        self.blockchain = Blockchain()
        self.blockchain.add_block(genesis_block)
        self.current_state = State({'0': {genesis_transaction_output.id: genesis_transaction_output}}, { genesis_transaction.transaction_id })
        self.shadow_log[genesis_block.hash] = deepcopy(self.current_state)
        
    def update_current_block(self):
        if self.current_block is not None:
            return
        
        # * This happens so that we has the most recent last block to get the hash from
        # * but in our scenario this is not really necessary because all nodes actually update their chains almost at the same time
        self.consensus()
        
        new_block = Block(self.blockchain.last_hash)
        self.active_blocks.append(new_block)
        self.current_block = new_block
        self.active_blocks_log[new_block.timestamp] = deepcopy(self.current_state)
        
    def validate_block(self, block: Block, current_state: State):        
        block_state = deepcopy(current_state)
                
        has_invalid_transaction = False
        for transaction in block.list_of_transactions:
            if self.validate_transaction(transaction, block_state) is False:
                has_invalid_transaction = True
                break
            else:
                was_already_processed = transaction.transaction_id in block_state.processed_transactions
                if not was_already_processed:
                    self.process_transaction(transaction, block_state)
            
        has_valid_hash = block.validate_hash()
        
        if has_valid_hash and not has_invalid_transaction:
            return True, block_state
        else:
            return False, None
        
    def validate_blockchain(self, partial_chain: Blockchain, last_consensual_block_hash: str):
        is_continuation_of_our_chain = partial_chain.chain[0].previous_hash == last_consensual_block_hash
        
        blockchains_shadow_log = {}
        
        is_last_consensual_block_in_our_blockchain = False
        for block in self.blockchain.chain:
            blockchains_shadow_log[block.hash] = deepcopy(self.shadow_log[block.hash])
            
            if last_consensual_block_hash == block.hash:
                is_last_consensual_block_in_our_blockchain = True
                break
            
        is_valid_chain_connection = is_continuation_of_our_chain and is_last_consensual_block_in_our_blockchain
        if not is_valid_chain_connection:
            return False, None
            
        current_state = deepcopy(blockchains_shadow_log[last_consensual_block_hash])
        previous_block_hash = last_consensual_block_hash
        for block in partial_chain.chain:
            is_block_valid, current_state = self.validate_block(block, current_state)
            is_chain = block.previous_hash == previous_block_hash
            previous_block_hash = block.hash
            
            if not (is_block_valid and is_chain):
                return False, None
            
            blockchains_shadow_log[block.hash] = deepcopy(current_state)
        
        return True, blockchains_shadow_log

    """
        Add block that we received from another node to our blockchain after checking its validity
    """    
    def add_block_to_blockchain(self, block: Block):
        is_valid_block, block_state = self.validate_block(block, self.current_state)
        is_next_block = self.blockchain.last_hash == block.hash
        
        if is_valid_block:
            if not is_next_block:
                self.consensus()
                return False
            else:
                self.blockchain.add_block(block)
                self.current_state = deepcopy(block_state)
                self.shadow_log[block.hash] = deepcopy(block_state)
                return True
                
    def consensus(self):
        chains = []
        for key in self.ring.keys():
            node_id = key
            node_ip = self.ring[key]['ip']
            node_port = self.ring[key]['port']
            
            if node_id != self.id:
                partial_chain, last_consensual_block_hash = blockchain_api.get_blockchain_from_node(node_ip, node_port)
                is_valid, blockchain_shadow_log = self.validate_blockchain(partial_chain, last_consensual_block_hash)
                if is_valid:
                    chain = Blockchain()
                    for block in self.blockchain.chain:
                        chain.add_block(block)
                        if block.hash == last_consensual_block_hash:
                            break
                    for block in partial_chain:
                        chain.add_block(block)
                    
                    chains.append({ 'chain': chain, 'shadow_log': blockchain_shadow_log })
            else:
                chains.append({ 'chain': self.blockchain, 'shadow_log': self.shadow_log })
                
        winner_chain = self.get_longest_chain(chains)
        
        
        # TODO: All these changes should happen as an atomic transaction
        self.blockchain: Blockchain = winner_chain['chain'] 
        self.shadow_log: dict[str, State] = winner_chain['shadow_log']
        self.current_state = self.shadow_log[self.blockchain.last_hash]
        self.wallet.UTXOs = [utxo for _, utxo in self.current_state.utxos[self.id].items()]
        
        # TODO: Potentially nuke active blocks if new chain was chosen
                
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
        self.update_current_block()
        
        receiver_public_key = self.ring[node_id]['public_key']
        active_state = self.active_blocks_log[self.current_block.timestamp]
        
        public_key, private_key = self.wallet.get_key_pair()
        my_UTXOs = [utxo for _, utxo in active_state.utxos[self.id].items()]
        
        transaction_inputs = [TransactionInput(UTXO) for UTXO in my_UTXOs]
        
        # Try creating it and handle the error of not having enough balance
        try:
            new_transaction = Transaction(public_key.decode(), receiver_public_key, amount=amount, transaction_inputs=transaction_inputs)
        except Exception as e:
            print(e)
            raise e
        
        # Sign the transaction
        new_transaction.sign_transaction(private_key)
        
        return new_transaction


    def process_transaction(self, transaction: Transaction, state: State):
        """Update state based on transaction

        Args:
            transaction (Transaction): The current transaction
            state (State): The state to be updated. WARNING: This must be a pointer to the state (if you are a pure python programmer dont get scared by reading the word pointer it doesnt bite)
        """        
        sender_address = transaction.sender_address
        recipient_address = transaction.recipient_address
        
        sender_node_id = self.get_node_id_from_address(sender_address)
        recipient_node_id = self.get_node_id_from_address(recipient_address)
        
        sender_transaction_output = transaction.get_sender_transaction_output()
        recipient_transaction_output = transaction.get_recipient_transaction_output()

        # * This only works because nodes following this code use all their UTXOs as trans inputs when creating a transaction
        state.utxos[sender_node_id] = {}

        state.utxos[sender_node_id][sender_transaction_output.id] = sender_transaction_output
        state.utxos[recipient_node_id][recipient_transaction_output.id] = recipient_transaction_output
        
        state.processed_transactions.add(transaction.transaction_id)

    def validate_transaction(self, transaction: Transaction, state: State):
        # 1. make sure that transaction signature is valid
        # 2. check that the sender node has enough balance based on its UTXOs
        # * Check that transaction is not already in blockchain
        is_not_already_processed = transaction.transaction_id not in state.processed_transactions
        
        # * Check that transaction is valid
        has_valid_signature = transaction.verify_signature()
        
        sender_address = transaction.sender_address       
        sender_node_id = self.get_node_id_from_address(sender_address)
        
        has_invalid_transaction_inputs = False
        for transaction_input in transaction.transaction_inputs:
            is_unspent_transaction = transaction_input.id in state.utxos[sender_node_id]
            
            if is_unspent_transaction is False:
                has_invalid_transaction_inputs = True
                break
        
        is_valid_transaction = is_not_already_processed and has_valid_signature and not has_invalid_transaction_inputs
        
        return is_valid_transaction

    def add_transaction_to_block(self, transaction: Transaction):
        self.mining_sem.acquire()
        
        # This creates a new block if one is not already active
        self.update_current_block()
        
        active_state = self.active_blocks_log[self.current_block.timestamp]
        
        is_valid = self.validate_transaction(transaction, active_state)
        
        if is_valid:
            self.process_transaction(transaction, active_state)
            
            self.current_block.add_transaction(transaction)
            
            if self.current_block.capacity == self.current_block.get_length():
                self.mine_current_block()
                
        self.mining_sem.release()

    # TODO: After 1st block starts mining, the second one needs to be created with the mining block's final state as its initial state and also with its timestamp as previous hash
    # TODO: Before starting mining check that our previous hash matches the current blocks hash or timestamp if not yeet us else replace previous hash with last blocks hash and 
    # TODO: then diggy diggy!

    # TODO: When you yeet a block, you have to run add_transaction_to_block for each transaction in the yeeted block and also broadcast them
    # TODO: Also check if a block is yeetable after mining is done, if not add it to the blockchain

    # TODO: Sometime we need to update (delete stuff) from the active logs
    
    # TODO: During consensus if i end up throwing away a chunk of my blockchain then these blocks may contain transaction that only i had so i should not yeet them before re-broadcasted said transactions
    def threaded_mining(self, current_block: Block, callback_function):
        self.mining_sem.acquire()
        self.mining_lock.acquire()
    
        mined_block = current_block.mine()
        
        callback_function(mined_block)
        
    def mining_end(self, mined_block: Block):
        # Check that mining was successful
        has_valid_hash = mined_block.validate_hash()
        
        is_next_in_chain = self.blockchain.last_hash == mined_block.previous_hash
        
        if has_valid_hash and is_next_in_chain:
            self.blockchain.add_block(mined_block)
            
            # Broadcast block
            block_api.broadcast_block(mined_block)
        
        self.mining_lock.release()
        self.mining_sem.release()
            
    def mine_current_block(self):
        # TODO: This should be running on another thread if you hate yourself
        # TODO: This stores the state(a state consists of all the data structures that change during transaction processing)
        # TODO: before we start mining because it is the final state of the block
        # TODO: which should be added to our shadow_log if this block ends up in the blockchain
        # * This holds the states of our currently mining blocks
        mining_thread = threading.Thread(target=self.threaded_mining, args=(self.current_block, self.mining_end))
        mining_thread.start()
        
        self.current_block = None
        
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

