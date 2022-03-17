import base64
import os

import Crypto
import requests
from Crypto.Hash import SHA256
from dotenv import load_dotenv
from flask import Flask, g, request

from noobcash.node import Node
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput
from noobcash.transaction_output import TransactionOutput

load_dotenv('../.env')

CAPACITY = int(os.getenv('CAPACITY'))
DIFFICULTY = int(os.getenv('DIFFICULTY'))

current_node: Node = None

def create_app():        
    app = Flask(__name__)
    
    from noobcash import root_api
    app.register_blueprint(root_api.bp)
    
    from noobcash import bootstrap_api
    app.register_blueprint(bootstrap_api.bp)
    
    from noobcash import transaction_api
    app.register_blueprint(transaction_api.bp)
    
    from noobcash import block_api
    app.register_blueprint(block_api.bp)
    
    from noobcash import blockchain_api
    app.register_blueprint(blockchain_api.bp)
    
    from noobcash import id_api
    app.register_blueprint(id_api.bp)
    
    from noobcash import ring_api
    app.register_blueprint(ring_api.bp)
    
    return app
            