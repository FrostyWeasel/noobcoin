import noobcash
from flask import Blueprint
from flask import request

from noobcash.transaction_output import TransactionOutput

bp = Blueprint('id', __name__, url_prefix='/id')
    
@bp.route('/id/post', methods=["POST"])
def id_post():    
    noobcash.current_node.id = int(request.form['node_id'])
    
    return '', 200

@bp.route('/id/get', methods=["GET"])
def id_get():    
    return f'{noobcash.current_node.id}', 200