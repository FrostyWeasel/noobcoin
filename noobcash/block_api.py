from flask import Blueprint, request
import noobcash

from noobcash.block import Block

bp = Blueprint('block', __name__, url_prefix='/block')

@bp.route('/receive', methods=['POST'])
def receive():
    received_block = Block.from_dictionary(dict(request.get_json()))
    
    # print(f'[/block/receive] Received transaction {received_block.to_dict()}')
    
    noobcash.current_node.add_block_to_blockchain(received_block)
    
    return '', 200
    
@bp.route('/genesis', methods=['POST'])
def genesis():
    genesis_block = Block.from_dictionary(dict(request.get_json()))
    
    # print(f'[/block/genesis] Genesis block {genesis_block.to_dict()}')
    
    noobcash.current_node.handle_genesis_block(genesis_block)
    
    return '', 200