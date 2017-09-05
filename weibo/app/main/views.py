#!/usr/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from datetime import datetime
from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import login_user,logout_user

from app.main import main
from forms import RegistForm,LoginForm
from app.models import Comments,User,Role,Weibo,Friends,Topic,topic_weibo
from app import db,login_manager

@login_manager.user_loader
def load_user(user_id):
    """ 登录回调"""
    return User.query.get(user_id)

@main.route('/')
def index():
    """ 微博首页 """
    return render_template('user/regist.html')

@main.route('/user/regist')
def regist():
    """注册页面"""
    form=RegistForm()
    if form.validate_on_submit():
        user = form.regist()
        # 登录用户
        login_user(user)
        # 消息提示
        flash('注册成功')
        # 跳转到首页
        return redirect(url_for('main.index'))


    return render_template('user/regist.html',form=form)

@main.route('/user/login')
def login():
    """登录页面"""
    form=LoginForm()
    if form.validate_on_submit():
        data=form.data
        user=User.query.filter_by(username=data["username"]).first()
        # 判断用户名是否存在
        if user is None:
            flash('用户不存在')
            return redirect(url_for('main.login'))
         # 登录用户
        login_user(user)
        # 保存用户的最后登录时间
        user.last_login = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("欢迎您: %s" % user.nickname)
        next_url = request.args.get('next')
        return redirect(next_url or url_for('main.index'))
    return render_template("user/login.html", form=form)

@main.route('/user/logout/', methods=['GET', 'POST'])
def logout():
    """ 退出登录 """
    logout_user()
    flash("感谢您的访问")
    return redirect(url_for('main.index'))