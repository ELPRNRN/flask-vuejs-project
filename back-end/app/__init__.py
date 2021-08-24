from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.expression import null
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from sqlalchemy import func
from datetime import datetime

import pymysql
pymysql.install_as_MySQLdb()

# Flask-SQLAlchemy plugin
db = SQLAlchemy()
# Flask-Migrate plugin
migrate = Migrate()
scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Shanghai"))
appForJob = null

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    global appForJob
    appForJob = app
    # Enable CORS
    CORS(app)
    # Init Flask-SQLAlchemy
    db.init_app(app)
    # Init Flask-Migrate
    migrate.init_app(app, db)

    # 注册 blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    scheduler.init_app(app)
    scheduler.start()

    return app

@scheduler.task('interval', id='job1', days=1, start_date='2021-8-20 23:59:30' , end_date='2022-8-20 23:59:30')
def addDaylyRecord():
    with appForJob.app_context():
        presentDate = datetime.now().isoformat()[0:10]
        if not DaylyRecord.query.filter_by(date = presentDate).first():
            totalAssets = Asset.query.count()
            spareAssets = Asset.query.filter(Asset.state =='空闲').count()
            inUseAssets = Asset.query.filter(Asset.state =='使用中').count()
            discardedAssets = Asset.query.filter(Asset.state =='已报废').count()
            applications = Application.query.filter(func.date_format(presentDate, "%Y-%m-%d") == func.date_format(Application.applytime, "%Y-%m-%d")).count()

            record = DaylyRecord()
            record.date = presentDate
            record.total_assets = totalAssets
            record.spare_assets = spareAssets
            record.in_user_assets = inUseAssets
            record.discarded_assets = discardedAssets
            record.applications = applications

            db.session.add(record)
            db.session.commit()

from app import models
from app.models import Asset, Application, DaylyRecord