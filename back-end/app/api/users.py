import re
from flask import json, request, jsonify, url_for
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import User
from app.api.auth import token_auth

@bp.route('/users', methods=['POST'])
def create_user():
    '''注册一个新用户'''
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')

    message = {}
    if 'username' not in data or not data.get('username', None):
        message['username'] = '请提供一个有效的用户名！'
    if 'password' not in data or not data.get('password', None):
        message['password'] = '请提供一个有效的密码！'
    if 'department' not in data or not data.get('department',None):
        message['department'] = '请选择你的部门！'
    if User.query.filter_by(username=data.get('username', None)).first():
        message['username'] = '请使用不同的用户名！'
    if message:
        return bad_request(message)

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    '''返回用户集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    '''返回一个用户'''
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    '''修改一个用户'''
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')
    message = {}
    if 'username' in data and not data.get('username', None):
        message['username'] = '请提供有效的用户名！'
    if 'department' in data and not data.get('department',None):
        message['department'] = '请提供有效的部门！'
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        message['username'] = '请使用不同的用户名！'
    if message:
        return bad_request(message)

    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/modifypassword/<int:id>', methods=['PUT'])
@token_auth.login_required
def modify_password(id):
    '''修改用户密码'''
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request('You must post JSON data.')
    message = {}
    if 'oldpassword' in data and not data.get('oldpassword', None):
        message['oldpassword'] = '请输入原密码！'
    if 'newpassword' in data and not data.get('newpassword',None):
        message['newpassword'] = '请输入新密码！'
    if 'oldpassword' in data and not user.check_password(data['oldpassword']):
        message['wrongpassword'] = '原密码错误！'
    if message:
        return bad_request(message)
    user.set_password(data['newpassword'])
    db.session.commit()
    return jsonify(user.to_dict())
    


@bp.route('/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    '''删除一个用户'''
    pass