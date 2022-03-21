from copy import deepcopy
import requests
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from Crypto.Hash import SHA256
import noobcash
from noobcash.block import Block
from noobcash.node import Node
from noobcash.transaction import Transaction
from noobcash.api.transaction_api import broadcast_transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

bp = Blueprint('bootstrap', __name__, url_prefix='/bootstrap')

@bp.route('/register', methods=['POST'])
def register():
    noobcash.master_lock.acquire()
    
    public_key = request.form['node_public_key']
    ip_address = request.form['node_ip_address']
    port = request.form['node_port']
    
    node_id = str(len(noobcash.current_node.ring))

    noobcash.current_node.ring[node_id] = {'ip': ip_address, 'port': port, 'id': node_id, 'public_key': public_key, 'UTXOs': {}}
            
    send_id_to_node(ip_address, port, node_id)
        
    if len(noobcash.current_node.ring) == int(os.getenv('NODE_NUM')):
        # print(f"[/bootstrap/register] I am about to send ring: {noobcash.current_node.ring}")
        # print(f"[/bootstrap/register] I am bootstrap and my wallet is: {[utxo.to_dict() for utxo in noobcash.current_node.wallet.UTXOs]}")
        broadcast_ring(noobcash.current_node.ring)
        broadcast_genesis(noobcash.current_node.current_block, noobcash.current_node.ring)
        
        noobcash.current_node.current_block = None
        
        for node_id in noobcash.current_node.ring.keys():
            if node_id != noobcash.current_node.id:
                new_transaction = noobcash.current_node.create_transaction(node_id, amount=100)
                broadcast_transaction(new_transaction)
                noobcash.current_node.add_transaction_to_block(new_transaction)
                
        noobcash.master_lock.release()
        return '', 200
    
    noobcash.master_lock.release()

    return '', 200

@bp.route('/reset', methods=['GET'])
def reset():        
    noobcash.current_node = Node()
    
    # Boostrap node duties:        
    noobcash.current_node.create_initial_blockchain()
    
    return '', 200

def send_id_to_node(node_address, node_port, node_id):
    r = requests.post(f"http://{node_address}:{node_port}/id/post", data={'node_id': node_id})

def broadcast_ring(ring):
    ring = ring_to_dict(ring)
    
    for key, node_info in ring.items():
        if key != noobcash.current_node.id:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/ring/post", json=ring)
            
def broadcast_genesis(genesis: Block, ring):
    genesis_block = genesis.to_dict()
    
    for key, node_info in ring.items():
        if key != noobcash.current_node.id:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/block/genesis", json=genesis_block)
            
def ring_to_dict(ring):
    new_ring = deepcopy(ring)
    
    for key, node_info in new_ring.items():
        utxos = node_info['UTXOs']
        new_utxos = {}
        for trans_id, utxo in utxos.items():
            new_utxos[trans_id] = utxo.to_dict()
        new_ring[key]['UTXOs'] = new_utxos
    
    return new_ring