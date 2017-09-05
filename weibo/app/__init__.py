#coding=utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
#from flaskflask_mail import Mail
#from flask_bootstrap import Bootstrap

#bootstrap = Bootstrap()
#mail = Mail()
db = SQLAlchemy()
#config_name='development'
login_manager = LoginManager()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #boostrap.init_app(app)
    #mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    db.init_app(app)

    #附加路由和自定义错误界面

#    from .main import main as main_blueprint
#    app.register_blueprint(main_blueprint)

    return app

#app = create_app(config_name)