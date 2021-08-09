import re
from flask import request, jsonify, url_for
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api import assets
from app.api.auth import token_auth
from app.models import Asset

@bp.route('/assets', methods=['POST'])
def create_asset():
    '''注册一个新用户'''
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')

    message = {}
    if 'assetname' not in data or not data.get('assetname', None):
        message['assetname'] = 'Please provide a valid assetname.'
    if 'registertime' not in data or not data.get('registertime', None):
        message['registertime'] = 'Please provide a valid registertime.'
    if 'department' not in data or not data.get('department',None):
        message['department'] = 'Please choose your department'
    if 'remarks' not in data or not data.get('remarks',None):
        message['remarks'] = 'Please provide your remarks'
    if message:
        return bad_request(message)

    asset = Asset()
    asset.from_dict(data, new_asset=True)
    db.session.add(asset)
    db.session.commit()
    response = jsonify(asset.to_dict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_user', id=asset.id)
    return response