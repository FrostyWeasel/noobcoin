import os
import requests
from noobcash.node import Node
from flask import Flask, request
from dotenv import load_dotenv
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput

from noobcash.transaction_output import TransactionOutput

# TODO: Clean up imports
# TODO: Handle node class persistance between api calls better

def create_app():
    load_dotenv('../.env')
        
    app = Flask(__name__)
    
    current_node: Node = None
        
    @app.route('/create_node', methods=["GET"])
    def create_node():
        global current_node
        
        port_number = os.getenv('FLASK_RUN_PORT')
        node_num = int(os.getenv('NODE_NUM'))
        
        current_node = Node()
        
        am_bootstrap = current_node.ring[0]['port'] == port_number
        
        if am_bootstrap is True:        
            genesis_transaction_ouput = TransactionOutput(current_node.wallet.public_key, 100*node_num, 0)
            genesis_transaction = Transaction(bytes(0), current_node.wallet.public_key, 100*node_num, [TransactionInput(genesis_transaction_ouput)])

            current_node.id = 0
            current_node.ring[0]['public_key'] = current_node.wallet.public_key.decode("utf-8") 
            current_node.ring[0]['id'] = 0
            
            current_node.ring[0]['UTXOs'] = [genesis_transaction_ouput]
    
            # TODO: make genesis block
            # TODO: add transaction to genesis block
        else:
            my_ip_address = os.getenv('IP_ADDRESS')
            while True:
                try:
                    r = requests.post(f"http://{current_node.ring[0]['ip']}:{current_node.ring[0]['port']}/bootstrap/register",
                                    data={'node_public_key': current_node.wallet.public_key.decode("utf-8"), 'node_ip_address': my_ip_address, 'node_port': port_number})
                    break
                except:
                    pass
                
        return '', 200
    
    @app.route('/bootstrap/register', methods=["POST"])
    def post():
        global current_node
        public_key = request.form['node_public_key']
        ip_address = request.form['node_ip_address']
        port = request.form['node_port']
        
        node_id = len(current_node.ring)
        
        current_node.ring.append({'ip': ip_address, 'port': port, 'public_key': public_key, 'id': node_id, 'UTXOs': []})
        
        send_id_to_node(ip_address, port, node_id)

        transaction = current_node.create_transaction(public_key, amount=100)
        # TODO: Add transaction to current blockchain block
        
        if len(current_node.ring) == int(os.getenv('NODE_NUM')):
            
            broadcast_ring(current_node.ring)
            # broadcast_blockchain()
            
            return '', 200
    
        return '', 200
    
    @app.route('/ring/post', methods=["POST"])
    def ring_post():
        global current_node
        current_node.ring = request.get_json()
        
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

def send_id_to_node(node_address, node_port, node_id):
    r = requests.post(f"http://{node_address}:{node_port}/id/post", data={'node_id': node_id})

def broadcast_ring(ring):
    for i, node_info in enumerate(ring):
        if i != 0:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/ring/post", json=ring)
            