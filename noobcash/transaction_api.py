import functools
import requests
import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import noobcash
import noobcash.transaction

bp = Blueprint('transaction', __name__, url_prefix='/transaction')

@bp.route('/receive', methods=['POST'])
def receive():
    return request.get_json(), 200
