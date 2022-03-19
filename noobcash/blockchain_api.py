import functools
import requests
import os
from noobcash.blockchain import Blockchain
from noobcash.transaction import Transaction

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('blockchain', __name__, url_prefix='/blockchain')

@bp.route('/get', methods=['GET'])
def get():
    return '', 200

# TODO: Error handling
def get_blockchain_from_node(node_ip, node_port):
    r = requests.get(f"http://{node_ip}:{node_port}/blockchain/get")
    
    chain = Blockchain.from_dictionary(r)
    return chain