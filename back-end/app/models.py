from operator import index
from sqlalchemy.sql.functions import register_function
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import url_for
import base64
from datetime import datetime, timedelta, date
import os

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class User(PaginatedAPIMixin, db.Model):

    __tablename__  = 'user'

    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # 不保存原始密码
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    role = db.Column(db.String(64))
    department = db.Column(db.String(64))
    applications = db.relationship('Application',backref=db.backref('user'))


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'department':self.department,
            'role':self.role,
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            }
        }
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['id','username', 'department','role']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
            self.role = 'user'

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

class Asset(PaginatedAPIMixin, db.Model):

    __tablename__  = 'asset'

    id = db.Column(db.Integer, primary_key=True, index=True)
    assetname = db.Column(db.String(64), index=True)
    registertime = db.Column(db.DateTime)
    department = db.Column(db.String(64))
    remarks = db.Column(db.String(64))
    state = db.Column(db.String(32))
    applications = db.relationship('Application',backref=db.backref('asset'))

    def __repr__(self):
        return '<Asset {}>'.format(self.assetname)

    def from_dict(self, data, new_asset=False):
        for field in ['id','assetname','department','remarks','state']:
            if field in data:
                setattr(self, field, data[field])
        if 'registertime' in data:
            setattr(self,'registertime',date.fromisoformat(data['registertime']))
        if new_asset:
            self.state = '空闲'

    def to_dict(self):
        data = {
            'id': self.id,
            'assetname': self.assetname,
            'registertime':self.registertime.isoformat()[:10],
            'department':self.department,
            'remarks':self.remarks,
            'state':self.state,
            '_links': {
                'self': url_for('api.get_asset', id=self.id)
            }
        }
        return data

class Application(PaginatedAPIMixin,db.Model):

    __tablename__  = 'application'

    id = db.Column(db.Integer, primary_key=True, index=True)
    assetid = db.Column(db.Integer,db.ForeignKey('asset.id'),index=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),index=True)
    applytime = db.Column(db.DateTime)
    expecttime = db.Column(db.DateTime)
    remarks = db.Column(db.String(64))
    state = db.Column(db.String(32))

    def __repr__(self):
        return '<Application {}>'.format(self.assetname)

    def from_dict(self, data, new_application=False):
        if('username' in data):
            applyuser = User.query.filter(User.username == data['username']).first()
            setattr(self,'userid',applyuser.id)
        for field in ['id','assetid','userid','remarks','state']:
            if field in data:
                setattr(self, field, data[field])
        for timefield in['expecttime','applytime']:
            if timefield in data:
                setattr(self,timefield,date.fromisoformat(data['expecttime']))
        if new_application:
            self.state = '审核中'
            self.applytime = datetime.now()
            

    def to_dict(self):
        data = {
            'id': self.id,
            'assetid': self.assetid,
            'assetname': self.asset.assetname,
            'assetstate': self.asset.state,
            'userid':self.userid,
            'username':self.user.username,
            'userdepartment':self.user.department,
            'applytime':self.applytime.isoformat()[:10],
            'expecttime':self.expecttime.isoformat()[:10],
            'remarks': self.remarks,
            'state':self.state,
            '_links': {
                'self': url_for('api.get_application', id=self.id)
            }
        }
        return data
