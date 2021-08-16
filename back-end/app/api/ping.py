from flask import jsonify
from app.api import bp


@bp.route('/ping', methods=['GET'])
def ping():
    '''前端Vue.js用来测试与后端Flask API的连通性'''
    return jsonify('Pong!')

@bp.route('/test', methods=['GET'])
def test():
    '''前端Vue.js用来测试与后端Flask API的连通性'''
    return jsonify('test!')