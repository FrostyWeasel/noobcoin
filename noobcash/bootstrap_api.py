import base64
import functools
import requests
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import Crypto
from Crypto.Hash import SHA256
import noobcash
from noobcash.node import Node
from noobcash.transaction import Transaction
from noobcash.transaction_api import broadcast_transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

bp = Blueprint('bootstrap', __name__, url_prefix='/bootstrap')

@bp.route('/register', methods=['POST'])
def register():    
    public_key = request.form['node_public_key']
    ip_address = request.form['node_ip_address']
    port = request.form['node_port']
    
    node_id = str(len(noobcash.current_node.ring))
    
    noobcash.current_node.ring[node_id] = {'ip': ip_address, 'port': port, 'id': node_id, 'public_key': public_key, 'UTXOs': {}}
            
    send_id_to_node(ip_address, port, node_id)
        
    if len(noobcash.current_node.ring) == int(os.getenv('NODE_NUM')):
        broadcast_ring(noobcash.current_node.ring)
        
        for node_id in noobcash.current_node.ring.keys():
            if node_id != noobcash.current_node.id:
                new_transaction = noobcash.current_node.create_transaction(node_id, amount=100)
                new_transaction_recipient_output = new_transaction.get_recipient_transaction_output()
                # TODO: Add transaction to current blockchain block

        # TODO: This only works with node num 2
        broadcast_transaction(new_transaction)
        
        # broadcast_blockchain()
        
        return '', 200

    return '', 200

@bp.route('/reset', methods=['GET'])
def reset():    
    node_num = int(os.getenv('NODE_NUM'))
    
    noobcash.current_node = Node()
    
    # Boostrap node duties:        
    genesis_transaction_ouput = TransactionOutput(noobcash.current_node.wallet.public_key.decode(), 100*node_num, base64.b64encode(SHA256.new(b'parent_id').digest()).decode('utf-8'))
    genesis_transaction = Transaction(Crypto.PublicKey.RSA.generate(2048).public_key().export_key().decode(), noobcash.current_node.wallet.public_key.decode("utf-8"), 100*node_num, [TransactionInput(genesis_transaction_ouput)])
    
    noobcash.current_node.wallet.UTXOs = []
    noobcash.current_node.wallet.add_transaction_output(genesis_transaction_ouput)

    noobcash.current_node.id = '0'
    noobcash.current_node.ring[noobcash.current_node.id]['id'] = noobcash.current_node.id
    noobcash.current_node.ring[noobcash.current_node.id]['UTXOs'] = { genesis_transaction_ouput.id: genesis_transaction_ouput }
    noobcash.current_node.ring[noobcash.current_node.id]['public_key'] = noobcash.current_node.wallet.public_key.decode()
    
    return '', 200

def send_id_to_node(node_address, node_port, node_id):
    r = requests.post(f"http://{node_address}:{node_port}/id/post", data={'node_id': node_id})

def broadcast_ring(ring):
    ring = utxos_to_dict(ring)
    
    for key, node_info in ring.items():
        if key != noobcash.current_node.id:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/ring/post", json=ring)
            
def utxos_to_dict(ring):
    for key, node_info in ring.items():
        utxos = node_info['UTXOs']
        new_utxos = {}
        for trans_id, utxo in utxos.items():
            new_utxos[trans_id] = utxo.to_dict()
        ring[key]['UTXOs'] = new_utxos
    
    return ring