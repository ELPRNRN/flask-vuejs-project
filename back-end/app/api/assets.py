import re
from flask import request, jsonify, url_for
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import Application, Asset
from app.api.auth import token_auth

@bp.route('/assets', methods=['POST'])
def create_asset():
    '''注册一个新资产'''
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
    response.headers['Location'] = url_for('api.get_asset', id=asset.id)
    
    return response

@bp.route('/assets', methods=['GET'])
@token_auth.login_required
def get_assets():
    '''返回资产集合'''
    page = request.args.get('page',1,type=int)
    per_page = min(request.args.get('per_page',5,type=int),100)
    assetid = request.args.get('assetid',0,type=int)
    department = request.args.get('department','',type=str)
    assetname = request.args.get('assetname','',type=str)
    state = request.args.get('state','',type=str)
    if(assetid == 0):
        data = Asset.to_collection_dict(
            Asset.query.filter(
                Asset.department.like('%'+department+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Asset.state.like('%'+state+'%')),
                page,per_page,
                'api.get_assets')
    else:
        data = Asset.to_collection_dict(
            Asset.query.filter(
                Asset.id == assetid,
                Asset.department.like('%'+department+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Asset.state.like('%'+state+'%')),
                page,per_page,
                'api.get_assets')
    #data = Asset.to_collection_dict(Asset.query,page,per_page,'api.get_assets')
    if data:
        response = jsonify(data)
        response.status_code = 200
        return response
    else:
        return bad_request('You must post JSON data.')
    
@bp.route('/assets/<int:id>', methods=['GET'])
@token_auth.login_required
def get_asset(id):
    '''返回一个资产'''
    return jsonify(Asset.query.get_or_404(id).to_dict())

@bp.route('/assets/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_asset(id):
    asset = Asset.query.get_or_404(id)
    data = request.get_json()
    message = {}
    if not data:
        return bad_request('You must post JSON data')
    if 'assetname' not in data or not data.get('assetname', None):
        message['assetname'] = 'Please provide a valid assetname.'
    if 'registertime' not in data or not data.get('registertime', None):
        message['registertime'] = 'Please provide a valid registertime.'
    if 'department' not in data or not data.get('department',None):
        message['department'] = 'Please choose asset department'
    if 'remarks' not in data or not data.get('remarks',None):
        message['remarks'] = 'Please provide your remarks'
    if 'state' not in data or not data.get('state',None):
        message['state'] = 'Please provide asset state'
    if message:
        return bad_request(message)
    
    asset.from_dict(data,new_asset=False)
    db.session.commit()
    return jsonify(asset.to_dict())


