import functools
import requests
import os
from noobcash.transaction import Transaction

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import noobcash
import noobcash.transaction

bp = Blueprint('transaction', __name__, url_prefix='/transaction')

@bp.route('/receive', methods=['POST'])
def receive():
    received_transaction = Transaction.from_dictionary(dict(request.get_json()))
    
    # print(f'[/transaction/receive] Received transaction {received_transaction.to_dict()}')
    
    noobcash.current_node.add_transaction_to_block(received_transaction)

    return str(received_transaction.to_dict() == dict(request.get_json())), 200

@bp.route('/create', methods=['POST'])
def create():
    recipient_node_id = request.form['recipient_id']
    amount = float(request.form['amount'])
    
    transaction = noobcash.current_node.create_transaction(recipient_node_id, amount)
    noobcash.current_node.add_transaction_to_block(transaction)
    broadcast_transaction(transaction)
    
    return '', 200
    
def broadcast_transaction(transaction: Transaction):
    for key, node_info in noobcash.current_node.ring.items():
        if key != noobcash.current_node.id:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/transaction/receive", json=transaction.to_dict())