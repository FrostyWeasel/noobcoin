from flask import Blueprint, request
import noobcash

from noobcash.block import Block

bp = Blueprint('block', __name__, url_prefix='/block')

@bp.route('/receive', methods=['POST'])
def receive():
    received_block = Block.from_dictionary(dict(request.get_json()))
    
    print(f'[/block/receive] Received transaction {received_block.to_dict()}')
    
    noobcash.current_node.add_block_to_blockchain(received_block)