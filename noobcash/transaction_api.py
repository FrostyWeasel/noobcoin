import functools
import requests
import os
from noobcash.transaction import Transaction

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import noobcash
import noobcash.transaction

bp = Blueprint('transaction', __name__, url_prefix='/transaction')

@bp.route('/receive', methods=['POST'])
def receive():
    received_transaction = Transaction.from_dictionary(dict(request.get_json()))
    
    noobcash.current_node.add_transaction_to_block(received_transaction)

    return str(received_transaction.to_dict() == dict(request.get_json())), 200
