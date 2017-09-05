#!/usr/bin/python
# #coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from __init__ import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user,UserMixin, current_user

import enum
class PermsEnum(enum.Enum):
    super_manager = "1"
    comment_manager = "2"
    weibo = "3"

class FriendEnum(enum.Enum):
    yes = "yes"
    no = "no"
    default = "default"

class User(UserMixin, db.Model):
    """ 用户 """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False, doc='用户名')
    password = db.Column(db.String(200), unique=True, nullable=False, doc='密码')
    nickname = db.Column(db.String(200), unique=True,  nullable=False, doc='昵称')
    head_img = db.Column(db.String(200), doc='个人头像地址')
    status = db.Column(db.Integer, default=1, doc='用户的状态')
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime, doc='最后登录时间')

    weibos = db.relationship('Weibo',backref='user',lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def set_password(self, password):
        """  设置用户的hash密码 """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """ 验证用户的password """
        return check_password_hash(self.password, password)

    def get_weibo_count(self):
        """ 发送微博的条数 """
        return Weibo.query.filter_by(user=self).count()

    def __repr__(self):
        return '<User %r>' % self.username


class Role(db.Model):
    """ 角色 """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    perms = db.Column(db.Enum(PermsEnum),doc="权限")
    is_valid = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Weibo(db.Model):
    """ 微博 """
    __tablename__ = 'weibo'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False,doc="微博内容")
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime,doc="创建时间")
    updated_at = db.Column(db.DateTime,doc="更新时间")

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    comments = db.relationship('Comments', backref='weibo',
                                lazy='dynamic')

    def __repr__(self):
        return '<Weibo %r>' % self.content


class Comments(db.Model):
    """ 微博评论 """

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000), nullable=False,doc="评论内容")

    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime,doc="创建时间")
    updated_at = db.Column(db.DateTime,doc="更新时间")

    weibo_id = db.Column(db.Integer, db.ForeignKey('weibo.id'))

    def __repr__(self):
        return '<Comments %r>' % self.content


class Friends(db.Model):
    """ 好友关系 """
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Enum(FriendEnum), doc='好友关系状态')
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


topic_weibo = db.Table('topic_weibo',
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')),
    db.Column('weibo_id', db.Integer, db.ForeignKey('weibo.id'))
)


class Topic(db.Model):
    """ 话题 """
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    head_img = db.Column(db.String(200), doc='缩略图')
    name = db.Column(db.String(64), nullable=False, unique=True)
    desc = db.Column(db.String(300))
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    weibos = db.relationship('Weibo', secondary=topic_weibo,
        backref=db.backref('weibos', lazy='dynamic'))
