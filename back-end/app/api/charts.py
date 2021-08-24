import re
from flask import json, request, jsonify, url_for
from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import Asset, DaylyRecord
from app.api.auth import token_auth
from sqlalchemy import func, desc

@bp.route('/charts', methods=['GET'])
@token_auth.login_required
def charts_data():
    '''获取表格数据'''
    totalAssets = Asset.query.count()
    spareAssets = Asset.query.filter(Asset.state =='空闲').count()
    inUseAssets = Asset.query.filter(Asset.state =='使用中').count()
    discardedAssets = Asset.query.filter(Asset.state =='已报废').count()
    pastRecords = DaylyRecord.query.order_by(desc(DaylyRecord.id)).limit(7).all()
    #[::-1]

    data = {
        'totalAssets' : totalAssets,
        'spareAssets' : spareAssets,
        'inUseAssets' : inUseAssets,
        'discardedAssets' :discardedAssets,
        'pastRecords': [item.to_dict() for item in pastRecords]
    }
    return jsonify(data)