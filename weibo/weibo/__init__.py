#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from settings import config

app = Flask(__name__)
app.config.from_object(config['default'])
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from weibo import views, models

