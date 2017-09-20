#!/usr/bin/python
#coding=utf-8


"""
表单类
参考文档：http://wtforms.readthedocs.io/en/latest/

字段类型            说明
StringField         文本字段
TextAreaField       多行文本字段
PasswordField       密码文本字段
HiddenField         隐藏文本字段
DateField           文本字段，值为datetime.date格式
DateTimeField       文本字段，值为datetime.datetime格式
IntegerField        文本字段，值为整数
DecimalField        文本字段，值为decimal.Decimal
FloatField          文本字段，值为浮点数
BooleanField        复选框，值为True和False
RadioField          一组单选框
SelectField         下拉列表
SelectMultipleField 下拉列表，可选择多个值
FileField           文件上传字段
SubmitField         表单提交按钮
FormField           把表单作为字段嵌入另一个表单
FieldList           一组指定类型的字段

"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re

from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,FileField
from wtforms.validators import DataRequired, ValidationError



from weibo import db
from weibo.models import User, Weibo, WeiboRelTopic, WeiboAtUser, Topic, Comment
from weibo import constants


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
    head_img = FileField(label="头像", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

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

    # def regist(self):
    #     """ 注册用户 """
    #     data = self.data
    #     f=data['head_img'].data
    #     filename=secure_filename(f.filename)
    #     addr=os.path.join(os.path.abspath(os.path.dirname(__file__)),filename)
    #     f.save(addr)
        # user = User(
        #     username=data['username'],
        #     nickname=data['nickname'],
        #     # head_img=addr,
        #     )
        # # 设置用户的密码
        # user.set_password(data['password'])
        # db.session.add(user)
        # db.session.commit()
        # 保存用户数据
        # 返回用户
        # return user


class WeiboForm(FlaskForm):
    """ 发送微博 """
    content = TextAreaField(label='微博内容', validators=[DataRequired("输入微博内容")],
        description="输入微博内容",
        render_kw={"required": "required", "class": "form-control"})
    submit = SubmitField('发布', render_kw={
            'class': 'btn btn-info'
        })

    def validate_content(self, field):
        """ 验证微博内容 """
        content = field.data
        if len(content) > 140:
            raise ValidationError('最长为140个字')
        if len(content) < 5:
            raise ValidationError('最少5个字')
        return content

    def publish(self, user):
        """ 发布微博 """
        data = self.data
        content = data['content']
        # 保存微博
        weibo_obj = Weibo(
            content=content,
            user=user,
            # user_id=user.id,微薄存在user的外建，导入user即可
            created_at=datetime.now()
            )
        db.session.add(weibo_obj)
        # 保存@关系
        at_users = re.findall(constants.AT_USER_PATTEN, content, re.MULTILINE)
        for nickname in at_users:
            user = User.query.filter_by(nickname=nickname).first()
            if user:
                weibo_at_user = WeiboAtUser(
                    weibo=weibo_obj,
                    user_id=user.id
                )
                db.session.add(weibo_at_user)
        # 保存话题关系
        topics = re.findall(constants.TOPIC_PATTEN, content, re.MULTILINE)
        print (topics)
        for name in topics:
            topic = Topic.query.filter_by(name=name).first()
            if topic is None:
                topic = Topic(
                    name=name,
                )
                db.session.add(topic)
            weibo_rel_topic = WeiboRelTopic(
                    topic=topic,
                    weibo=weibo_obj
                )
            db.session.add(weibo_rel_topic)
        db.session.commit()
        return weibo_obj


class WeiboCommentForm(FlaskForm):
    """ 微博评论 """
    content = StringField(label='微博评论', validators=[DataRequired("输入微博评论")],
        description="输入微博评论",
        render_kw={"required": "required", "class": "form-control"})
    submit = SubmitField('评论', render_kw={
            'class': 'btn btn-info pull-right'
        })

    def add_comment(self, weibo, user):
        """ 添加评论 """
        # 构建评论对象
        comment = Comment(
            user_id=user.id,
            weibo_id=weibo.id,
            content=self.data['content'],
            created_at=datetime.now()
        )
        db.session.add(comment)
        db.session.commit()
        return comment