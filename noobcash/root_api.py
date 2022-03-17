import base64
import os

import Crypto
import requests
from Crypto.Hash import SHA256
from flask import Blueprint, request

import noobcash
from noobcash.node import Node
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

bp = Blueprint('root', __name__, url_prefix='/')
    
@bp.route('/create_node', methods=["GET"])
def create_node():
    # Learn my port number and the number of maximum nodes
    port_number = os.getenv('FLASK_RUN_PORT')
    node_num = int(os.getenv('NODE_NUM'))
    
    noobcash.current_node = Node()
    
    # At the beginning only ring element contains the info of the bootstrap node
    # so we check if we are the bootstrap
    am_bootstrap = noobcash.current_node.ring['0']['port'] == port_number
    
    if am_bootstrap is True:
        # Boostrap node duties:        
        genesis_transaction_ouput = TransactionOutput(noobcash.current_node.wallet.public_key.decode(), 100*node_num, base64.b64encode(SHA256.new(b'parent_id').digest()).decode('utf-8'))
        genesis_transaction = Transaction(Crypto.PublicKey.RSA.generate(2048).public_key().export_key().decode(), noobcash.current_node.wallet.public_key.decode("utf-8"), 100*node_num, [TransactionInput(genesis_transaction_ouput)])
        
        noobcash.current_node.wallet.UTXOs = []
        noobcash.current_node.wallet.add_transaction_output(genesis_transaction_ouput)

        noobcash.current_node.id = '0'
        noobcash.current_node.ring[noobcash.current_node.id]['id'] = noobcash.current_node.id
        noobcash.current_node.ring[noobcash.current_node.id]['UTXOs'] = { genesis_transaction_ouput.id: genesis_transaction_ouput }
        noobcash.current_node.ring[noobcash.current_node.id]['public_key'] = noobcash.current_node.wallet.public_key.decode()

        # TODO: make genesis block
        # TODO: add transaction to genesis block
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
