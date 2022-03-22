from flask import Blueprint, request
import noobcash
import requests
from noobcash.api.ring_api import ring_from_dict

from noobcash.block import Block

bp = Blueprint('block', __name__, url_prefix='/block')

@bp.route('/receive', methods=['POST'])
def receive():
    noobcash.master_lock.acquire()
    
    received_block = Block.from_dictionary(dict(request.get_json()))    
    noobcash.current_node.add_block_to_blockchain(received_block)
    
    noobcash.master_lock.release()
    
    return '', 200
    
@bp.route('/genesis', methods=['POST'])
def genesis():
    noobcash.master_lock.acquire()
    
    genesis_block = Block.from_dictionary(dict(request.get_json())['genesis'])
    shadow_log = dict(request.get_json())['shadow_log']
    shadow_log['ring'] = ring_from_dict(shadow_log['ring'])
    
    # print(f'[/block/genesis] Genesis block {genesis_block.to_dict()}')
    
    noobcash.current_node.handle_genesis_block(genesis_block)
    
    noobcash.master_lock.release()
    
    return '', 200

def broadcast_block(block: Block, ring):
    block = block.to_dict()
    
    for key, node_info in ring.items():
        if key != noobcash.current_node.id:
            r = requests.post(f"http://{node_info['ip']}:{node_info['port']}/block/receive", json=block)