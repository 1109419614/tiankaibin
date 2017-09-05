#!/usr/bin/python
#coding=utf-8
import re
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, TextAreaField
from wtforms.validators import DataRequired,ValidationError

from app import db
from ..models import User
from app import constants

class LoginForm(FlaskForm):
    """ 登录表单 """
    username = StringField(label='用户名', validators=[DataRequired("请输入用户名")],
        description="请输入用户名",
        render_kw={"required": "required", "class": "form-control"})
    password = PasswordField(label='密码', validators=[DataRequired("请输入密码")],
        description="请输入密码",
        render_kw={"required": "required", "class": "form-control"})
    submit = SubmitField('登录', render_kw={
            'class': 'btn btn-info'
        })



class RegistForm(FlaskForm):
    """ 用户注册 """

    username = StringField(label="用户名", validators=[DataRequired()],
        render_kw={"required": 'required', "placeholder": "请输入用户名"},
        description="输入用用户邮箱注册")

    nickname = StringField(label="昵称", validators=[DataRequired()],
        render_kw={"required": 'required', "placeholder": "请输入昵称"},
        description="输入用户昵称")
    password = PasswordField('密码', validators=[DataRequired("请输入密码")])
    submit = SubmitField('注册', render_kw={
            'class': 'btn btn-info'
        })

    def validate_password(self, field):
        password = field.data
        if len(password) != 6:
            raise ValidationError("密码必须是6位")
        return password

    def validate_username(self, field):
        username = field.data.lower()
        # 判断改用户名是否已经存在
        user = User.query.filter_by(username=username).first()
        if user is not None:
            raise ValidationError("该用户已经注册")
        # 用户名必须是邮箱
        if not re.search(constants.EMAIL_PATTERN, username):
            raise ValidationError('请用邮箱注册')
        return username

    def validate_nickname(self, field):
        nickname = field.data.strip()
        # 判断改用户名是否已经存在
        exists_user = User.query.filter_by(nickname=nickname).count()
        if exists_user > 0:
            raise ValidationError("该用户昵称注册")
        # 昵称正则验证
        if not re.search(constants.UNICODE_PATTERN, nickname):
            raise ValidationError('昵称只能包含字母_-数字')
        return nickname

    def regist(self):
        """ 注册用户 """
        data = self.data
        user = User(
            username=data['username'],
            nickname=data['nickname'],
            created_at=datetime.now()
            )
        # 设置用户的密码
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        # 保存用户数据
        # 返回用户
        return user