import base64
from email.errors import NoBoundaryInMultipartDefect
import os

import Crypto
import requests
from Crypto.Hash import SHA256
from flask import Blueprint, request

import noobcash
from noobcash.block import Block
from noobcash.node import Node
from noobcash.state import State
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

bp = Blueprint('root', __name__, url_prefix='/')
    
@bp.route('/create_node', methods=["GET"])
def create_node():
    # Learn my port number and the number of maximum nodes
    port_number = os.getenv('FLASK_RUN_PORT')
    
    noobcash.current_node = Node()
    
    # At the beginning only ring element contains the info of the bootstrap node
    # so we check if we are the bootstrap
    am_bootstrap = noobcash.current_node.ring['0']['port'] == port_number
    
    if am_bootstrap is True:
        # Boostrap node duties:
        noobcash.current_node.create_initial_blockchain()
        
    else:
        my_ip_address = os.getenv('IP_ADDRESS')
        while True:
            try:
                r = requests.post(f"http://{noobcash.current_node.ring['0']['ip']}:{noobcash.current_node.ring['0']['port']}/bootstrap/register",
                                data={'node_public_key': noobcash.current_node.wallet.public_key.decode("utf-8"), 'node_ip_address': my_ip_address, 'node_port': port_number})
                break
            except:
                pass
            
    return '', 200

@bp.route('/info', methods=['GET'])
def info():
    active_state = noobcash.current_node.active_blocks_log[noobcash.current_node.active_block.timestamp] if noobcash.current_node.active_block is not None\
                else noobcash.current_node.current_state
    
    info = {
        'id': noobcash.current_node.id,
        'balance': noobcash.current_node.wallet.balance(),
        'wallet_utxos': [utxo.to_dict() for utxo in noobcash.current_node.wallet.UTXOs],
        'active_balance': sum([utxo for _, utxo in active_state.utxos[noobcash.current_node.id].items()]),
        'active_utxos': [utxo.to_dict() for _, utxo in active_state.utxos[noobcash.current_node.id].items()],
        'active_block': noobcash.current_node.active_block.to_dict() if noobcash.current_node.active_block is not None else {},
        'ring': noobcash.current_node.ring,
        'blockchain': noobcash.current_node.blockchain.to_dict(),
        'current_state': noobcash.current_node.current_state.to_dict(),
        'active_state': active_state.to_dict()
    }
    
    return info, 200

@bp.route('/initial_data', methods=['POST'])
def initial_data():
    data = request.get_json()
    
    ring = data['ring']
    genesis_block = Block.from_dictionary(data['genesis_block'])
    shadow_log = {key: State.from_dictionary(state) for key, state in data['shadow_log'].items()}

    noobcash.current_node.ring = ring
    noobcash.current_node.blockchain.add_block(genesis_block)
    noobcash.current_node.shadow_log = shadow_log
    noobcash.current_node.current_state = shadow_log[noobcash.current_node.blockchain.last_hash]
    
    return '', 200