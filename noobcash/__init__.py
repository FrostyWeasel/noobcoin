import os
import requests
from . import node as nd
from flask import Flask, request
from dotenv import load_dotenv
from noobcash.transaction import Transaction
from noobcash.transaction_input import TransactionInput

from noobcash.transaction_output import TransactionOutput

node = None

def create_app():
    load_dotenv('../.env')
        
    app = Flask(__name__)
    
    print(os.getenv('FLASK_RUN_PORT'))
    
    @app.route('/create_node', methods=["GET"])
    def create_node():
        global node
        
        port_number = os.getenv('FLASK_RUN_PORT')
        node_num = int(os.getenv('NODE_NUM'))
        
        me = nd.Node()
        node = me
        
        am_bootstrap = me.ring[0]['port'] == port_number
        
        if am_bootstrap is True:        
            genesis_transaction = Transaction(bytes(0), me.wallet.public_key, 100*node_num, [TransactionInput(TransactionOutput(me.wallet.public_key, 100*node_num, 0))])

            me.id = 0
            me.ring[0]['public_key'] = me.wallet.public_key.decode("utf-8") 
            me.ring[0]['id'] = 0
            
            # add transaction to genesis block
        else:
            my_ip_address = os.getenv('IP_ADDRESS')
            while True:
                try:
                    r = requests.post(f"http://{me.ring[0]['ip']}:{me.ring[0]['port']}/contact",
                                    data={'node_public_key': me.wallet.public_key.decode("utf-8"), 'node_ip_address': my_ip_address, 'node_port': port_number})
                    break
                except:
                    pass
                
            print('I got the contact response')

        return '', 200
    
    @app.route('/contact', methods=["POST"])
    def post():
        global node
        public_key = request.form['node_public_key']
        ip_address = request.form['node_ip_address']
        port = request.form['node_port']
        
        node_id = len(node.ring)
        
        node.ring.append({'ip': ip_address, 'port': port, 'public_key': public_key, 'id': node_id})
        
        send_id_to_node(ip_address, port, node_id)
        
        if len(node.ring) == int(os.getenv('NODE_NUM')):
            
            broadcast_ring(node.ring)
            # create_transaction()
            # broadcast_blockchain()
            
            return '', 200
    
        return '', 200
    
    @app.route('/ring/post', methods=["POST"])
    def ring_post():
        global node
        node.ring = request.get_json()
        
        return '', 200
    
    @app.route('/id/post', methods=["POST"])
    def id_post():
        global node
        node.id = int(request.form['node_id'])
        print('Daddy just send me my node id {node.id}')
        
        return '', 200
    
    @app.route('/id/get', methods=["GET"])
    def id_get():
        global node
        
        return f'{node.id}', 200

    return app

def send_id_to_node(node_address, node_port, node_id):
    r = requests.post(f"http://localhost:{node_port}/id/post", data={'node_id': node_id})

def broadcast_ring(ring):
    for i, node_info in enumerate(ring):
        if i != 0:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/ring/post", json=ring)
            