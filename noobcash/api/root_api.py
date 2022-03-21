import base64
import os

import Crypto
import requests
from Crypto.Hash import SHA256
from flask import Blueprint, request

import noobcash
from noobcash.block import Block
from noobcash.node import Node
from noobcash.api.bootstrap_api import ring_to_dict
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
    info = {
        'id': noobcash.current_node.id,
        'balance': noobcash.current_node.wallet.balance(),
        'wallet_utxos': [utxo.to_dict() for utxo in noobcash.current_node.wallet.UTXOs],
        'processed_transactions': list(noobcash.current_node.processed_transactions),
        'current_block': noobcash.current_node.current_block.to_dict() if noobcash.current_node.current_block is not None else {},
        'ring': ring_to_dict(noobcash.current_node.ring),
        'blockchain': noobcash.current_node.chain.to_dict()
    }
    
    return info, 200
