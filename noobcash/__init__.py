import base64
import os
import requests
from noobcash.node import Node
from flask import Flask, request, g
from dotenv import load_dotenv
import Crypto
from Crypto.Hash import SHA256
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput

from noobcash.transaction_output import TransactionOutput

# TODO: Clean up imports
# TODO: Handle node class persistance between api calls better

load_dotenv('../.env')

CAPACITY = int(os.getenv('CAPACITY'))

current_node: Node = None

def create_app():
    global current_node
        
    app = Flask(__name__)
    
    from noobcash import bootstrap_api
    app.register_blueprint(bootstrap_api.bp)
    
    from noobcash import transaction_api
    app.register_blueprint(transaction_api.bp)
            
    @app.route('/create_node', methods=["GET"])
    def create_node():
        global current_node

        # Learn my port number and the number of maximum nodes
        port_number = os.getenv('FLASK_RUN_PORT')
        node_num = int(os.getenv('NODE_NUM'))
        
        current_node = Node()
        
        # At the beginning only ring element contains the info of the bootstrap node
        # so we check if we are the bootstrap
        am_bootstrap = current_node.ring['0']['port'] == port_number
        
        if am_bootstrap is True:
            # Boostrap node duties:        
            genesis_transaction_ouput = TransactionOutput(current_node.wallet.public_key.decode(), 100*node_num, base64.b64encode(SHA256.new(b'parent_id').digest()).decode('utf-8'))
            genesis_transaction = Transaction(Crypto.PublicKey.RSA.generate(2048).public_key().export_key().decode(), current_node.wallet.public_key.decode("utf-8"), 100*node_num, [TransactionInput(genesis_transaction_ouput)])
            
            current_node.wallet.UTXOs = []
            current_node.wallet.add_transaction_output(genesis_transaction_ouput)

            current_node.id = '0'
            current_node.ring[current_node.id]['id'] = current_node.id
            current_node.ring[current_node.id]['UTXOs'] = { genesis_transaction_ouput.id: genesis_transaction_ouput }
            current_node.ring[current_node.id]['public_key'] = current_node.wallet.public_key.decode()
    
            # TODO: make genesis block
            # TODO: add transaction to genesis block
        else:
            my_ip_address = os.getenv('IP_ADDRESS')
            while True:
                try:
                    r = requests.post(f"http://{current_node.ring['0']['ip']}:{current_node.ring['0']['port']}/bootstrap/register",
                                    data={'node_public_key': current_node.wallet.public_key.decode("utf-8"), 'node_ip_address': my_ip_address, 'node_port': port_number})
                    break
                except:
                    pass
                
        return '', 200
    
    @app.route('/ring/post', methods=["POST"])
    def ring_post():
        global current_node
        
        ring = request.get_json()
        
        ring = utxos_from_dict(ring)
        
        current_node.ring = ring
        
        return '', 200
    
    @app.route('/id/post', methods=["POST"])
    def id_post():
        global current_node
        
        current_node.id = int(request.form['node_id'])
        
        return '', 200
    
    @app.route('/id/get', methods=["GET"])
    def id_get():
        global current_node
        
        return f'{current_node.id}', 200

    return app

def utxos_from_dict(ring):
    for key, node_info in ring.items():
        utxos = node_info['UTXOs']
        new_utxos = {}
        for trans_id, utxo in utxos.items():
            new_utxos[trans_id] = TransactionOutput.from_dictionary(utxo)
        ring[key]['UTXOs'] = new_utxos
    
    return ring
            