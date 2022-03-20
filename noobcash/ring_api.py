import noobcash
from flask import Blueprint
from flask import request

from noobcash.transaction_output import TransactionOutput

bp = Blueprint('ring', __name__, url_prefix='/ring')

@bp.route('/get', methods=['GET'])
def get():
    return '', 200

@bp.route('/post', methods=["POST"])
def post():    
    ring = request.get_json()
    
    # print(f"[/ring/post] I received ring: {ring}")
    
    ring = ring_from_dict(ring)
        
    noobcash.current_node.ring = ring
    
    return '', 200

def ring_from_dict(ring):
    for key, node_info in ring.items():
        utxos = node_info['UTXOs']
        new_utxos = {}
        for trans_id, utxo in utxos.items():
            new_utxos[trans_id] = TransactionOutput.from_dictionary(utxo)
        ring[key]['UTXOs'] = new_utxos
    
    return ring