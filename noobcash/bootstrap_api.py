import functools
import requests
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import noobcash
import noobcash.transaction

bp = Blueprint('bootstrap', __name__, url_prefix='/bootstrap')

@bp.route('/register', methods=['POST'])
def register():    
    public_key = request.form['node_public_key']
    ip_address = request.form['node_ip_address']
    port = request.form['node_port']
    
    node_id = len(noobcash.current_node.ring)
        
    send_id_to_node(ip_address, port, node_id)

    new_transaction = noobcash.current_node.create_transaction(public_key.encode('utf-8'), amount=100)
    new_transaction_recipient_output = new_transaction.get_recipient_transaction_output()
    # TODO: Add transaction to current blockchain block
    
    noobcash.current_node.ring[public_key] = {'ip': ip_address, 'port': port, 'id': node_id, 'UTXOs': {new_transaction_recipient_output.id: new_transaction_recipient_output}}
    
    if len(noobcash.current_node.ring) == int(os.getenv('NODE_NUM')):
        
        broadcast_ring(noobcash.current_node.ring)
        # broadcast_blockchain()
        
        return '', 200

    return '', 200

def send_id_to_node(node_address, node_port, node_id):
    r = requests.post(f"http://{node_address}:{node_port}/id/post", data={'node_id': node_id})

def broadcast_ring(ring):
    for i, node_info in enumerate(ring):
        if i != 0:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/ring/post", json=ring)