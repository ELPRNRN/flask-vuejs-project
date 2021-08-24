import re
from flask import request, jsonify, url_for
from werkzeug.wrappers import response
from app import db
import app
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Application, Asset, User
from sqlalchemy import desc

@bp.route('/applications', methods=['POST'])
@token_auth.login_required
def creat_application():
    '''添加一个申请'''
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')
    
    message = {}
    if 'assetid' not in data or not data.get('assetid', None):
        message['assetid'] = '请提供有效的资产编号！'
    if 'username' not in data or not data.get('username', None):
        message['username'] = '请提供有效的用户名！'
    if 'expecttime' not in data or not data.get('expecttime',None):
        message['expecttime'] = '请输入使用期限！'
    if  Asset.query.get_or_404(data['assetid']).state in ['使用中','已报废']:
        message['assetdisable'] = '资产使用中或已报废，无法进行申请！'
    
    if message:
        return bad_request(message)
    
    application = Application()
    application.from_dict(data, new_application =True)
    db.session.add(application)
    db.session.commit()
    response = jsonify(application.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_application',id= application.id)
    
    return response

@bp.route('/applications', methods=['GET'])
@token_auth.login_required
def get_applications():
    '''返回申请集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 5, type=int), 100)
    applicationid = request.args.get('applicationid', 0, type=int)
    assetid = request.args.get('assetid', 0, type=int)
    assetname = request.args.get('assetname', '', type=str)
    applyuser = request.args.get('applyuser', '', type=str)
    state = request.args.get('state','',type=str)
    #data = Application.to_collection_dict(Application.query, page, per_page, 'api.get_applications')
    if(applicationid == 0 and assetid==0):
        data = Application.to_collection_dict(
            Application.query.join(User).join(Asset).filter(
                User.username.like('%'+applyuser+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Application.state.like('%'+state+'%')).order_by(desc(Application.id)),
                page,
                per_page,
                'api.get_applications')
    elif(applicationid ==0 and assetid !=0):
        data = Application.to_collection_dict(
            Application.query.join(User).join(Asset).filter(
                Application.assetid == assetid,
                User.username.like('%'+applyuser+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Application.state.like('%'+state+'%')).order_by(desc(Application.id)),
            page,
            per_page,
            'api.get_applications')
    elif(applicationid !=0 and assetid ==0):
        data = Application.to_collection_dict(
            Application.query.join(User).join(Asset).filter(
                Application.id == applicationid,
                User.username.like('%'+applyuser+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Application.state.like('%'+state+'%')).order_by(desc(Application.id)),
            page,
            per_page,
            'api.get_applications')
    elif(applicationid !=0 and assetid !=0):
         data = Application.to_collection_dict(
            Application.query.join(User).join(Asset).filter(
                Application.id == applicationid,
                Application.assetid ==assetid,
                User.username.like('%'+applyuser+'%'),
                Asset.assetname.like('%'+assetname+'%'),
                Application.state.like('%'+state+'%')).order_by(desc(Application.id)),
            page,
            per_page,
            'api.get_applications')

    if data:
        response = jsonify(data)
        response.status_code = 200
        return response
    else:
        return bad_request('You must post JSON data.')

@bp.route('/applications/<int:id>', methods=['GET'])
@token_auth.login_required
def get_application(id):
    '''返回一个申请'''
    return jsonify(Application.query.get_or_404(id).to_dict())

@bp.route('/applications/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_application(id):
    '''修改一个申请'''
    application = Application.query.get_or_404(id)
    data = request.get_json()
    message = {}
    if not data:
        return bad_request('You must post JSON data')
    if 'state' in data and not data.get('state',None):
        message['operation'] = '请提供一个有效操作！'
    if(data['state'] == '已同意'):
        if(application.asset.state in ['使用中','已报废']):
            message['assetDisabled'] = '资产正在使用中或已报废，无法同意申请！'
        if(application.state == '已同意'):
            message['applicationAgreed'] = '该申请已被同意！'
        elif(application.state == '已拒绝'):
            message['applicationDisagreed'] = '该申请已被拒绝！'
    elif(data['state']=='已拒绝'):
        if(application.state == '已同意'):
            message['applicationAgreed'] = '该申请已被同意！'
        elif(application.state == '已拒绝'):
            message['applicationDisagreed'] = '该申请已被拒绝！'
    elif(data['state']=='已报废'):
        if(application.state == '已报废'):
            message['applicationDiscarded'] = '该资产已经报废！'
    elif(data['state']=='已回收'):
        if(application.state == '已回收'):
            message['applicationRetrieved'] = '该资产已被回收！'
    if message:
        return bad_request(message)
    
    application.from_dict(data,new_application=False)
    if(data['state']=='已同意'):
        application.asset.state = '使用中'
    elif(data['state']=='已报废'):
        application.asset.state = '已报废'
    elif(data['state']=='已回收'):
        application.asset.state = '空闲'
    db.session.commit()
    return jsonify(application.to_dict())


@bp.route('/userOperationWithApplication/<int:id>', methods=['PUT'])
@token_auth.login_required
def user_operate_application(id):
    '''用户申请回收或报废或取消'''
    application = Application.query.get_or_404(id)
    data = request.get_json()
    message = {}
    if not data:
        return bad_request('You must post JSON data')
    if 'state' in data and not data.get('state',None):
        message['operation'] = '请提供一个有效操作！'
    if(data['state'] == '已取消'):
        if(application.state == '已同意'):
            message['applicationAgreed'] = '该申请已被同意！'
        elif(application.state == '已拒绝'):
            message['applicationDisagreed'] = '该申请已被拒绝！'
    if message:
        return bad_request(message)
    
    application.from_dict(data,new_application=False)
    db.session.commit()
    return jsonify(application.to_dict())
    