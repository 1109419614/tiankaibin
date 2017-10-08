#!/usr/bin/python
#coding=utf-8

"""
view 层
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
from datetime import datetime
from flask import render_template, redirect, flash, url_for, request, abort,session
from flask_login import login_required, login_user, logout_user,\
    UserMixin, current_user
from werkzeug.utils import secure_filename

from weibo.forms import LoginForm, RegistForm, WeiboForm, WeiboCommentForm,ChangepwdForm
from weibo import login_manager, db, app
from weibo.models import User, Weibo, Topic, WeiboRelTopic, Comment, Role,Friend
from weibo.decorators import staff_perms_required
from weibo import constants


@login_manager.user_loader
def load_user(user_id):
    """ 登录回调"""
    return User.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/page/<int:page>/')
def index(page=None):
    """ 新闻首页 发微博"""
    form = WeiboForm()
    if form.validate_on_submit():
        # 判断用户是否已经登录
        if current_user.is_authenticated:
            # 保存微博
            form.publish(user=current_user)
            # 提示消息
            flash("发布成功！")
            # 跳转到首页
            return redirect(url_for('index'))
        else:
            flash('请先登录')
            return redirect(url_for('login'))
    if page is None:
        page = 1
    page_data = Weibo.query.filter_by(is_valid=1)\
        .order_by(Weibo.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('home/index.html',
        form=form,
        page_data=page_data)


@app.route('/user/login/', methods=['GET', 'POST'])
def login():
    """ 登录 """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(username=data['username']).first()
        # 判断用户名是否存在
        if user is None:
            flash('用户不存在')
            return redirect(url_for('login'))
        # 判断密码是否正确
        if not user.check_password(data['password']):
            flash('密码不正确')
            return redirect(url_for('login'))
        # 登录用户
        login_user(user)
        # 保存用户的最后登录时间
        user.loast_login = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("欢迎您: %s" % user.nickname)
        next_url = request.args.get('next')
        return redirect(next_url or url_for('index'))
    return render_template("user/login.html", form=form)


@app.route('/user/logout/', methods=['GET', 'POST'])
def logout():
    """ 退出登录 """
    logout_user()
    flash("感谢您的访问")
    return redirect(url_for('index'))


@app.route('/user/regist/', methods=['GET', 'POST'])
def regist():
    """ 注册 """
    form = RegistForm()
    if form.validate_on_submit():
        f = form.head_img.data
        filename = secure_filename(f.filename)
        addr = os.path.join("head_img", filename)
        f.save(addr)
        user = User(
            username=form.data['username'],
            nickname=form.data['nickname'],
            head_img=addr,
        )
        # 设置用户的密码
        user.set_password(form.data['password'])
        db.session.add(user)
        db.session.commit()
        # user = form.regist()
        # 登录用户
        login_user(user)
        # 消息提示
        flash('注册成功')
        # 跳转到首页
        return redirect(url_for('index'))
    return render_template('user/regist.html', form=form)

@app.route('/user/changepwd/', methods=['GET', 'POST'])
@login_required
def changepwd():
    """ 修改密码 """
    form=ChangepwdForm()
    if form.validate_on_submit():
        if current_user.check_password(form.data['oldpassword']):
            current_user.set_password(form.data['newpassword'])
            db.session.add(current_user)
            db.session.commit()
            flash('你的密码成功修改啦')
            return redirect(url_for('index'))
        else:
            flash('修改失败,请确认旧密码正确')

    return render_template('user/changepwd.html',form=form)


@app.route('/user/profile/<nickname>/')
@login_required
def profile(nickname):
    """ 个人用户详细信息 """
    user = User.query.filter_by(nickname = nickname).first_or_404()
    #print(current_user)
    return render_template('user/profile.html',user=user)

@app.route('/user/attention')
@app.route('/user/attention/page/<int:page>')
@login_required
def attention(page=None):
    """ 关注好友 """
    if page is None:
        page = 1
    #注意下行的"==",filter与filter_by差别

    page_data =User.query.join(Friend,User.id == Friend.from_user_id).order_by(User.created_at.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('user/attention.html',page_data=page_data)

@app.route('/user/<nickname>/')
@app.route('/user/<nickname>/page/<int:page>/')
def user_detail(nickname, page=None):
    """ 根据用户的昵称查看用户的信息 """
    user = User.query.filter_by(nickname=nickname).first_or_404()
    # 该用户的所有微博
    # 方式一
    # page_data = Weibo.query.filter_by(
    #     user=user, is_valid=1
    #     ).order_by(Weibo.created_at.desc())\
    #     .paginate(page=page, per_page=10)

    # 方式二
    # 模型中需要添加 lazy='dynamic'
    page_data = user.weibos.filter(
        Weibo.is_valid==1
        ).order_by(Weibo.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('home/user.html',
        user=user,
        page_data=page_data)


@app.route('/topic/detail/<name>/')
@app.route('/topic/detail/<name>/page/<int:page>/')
def topic_detail(name, page=None):
    """ 根据话题名称查看详情 """
    form = WeiboForm(data={'content': "#%s#" % name})
    if page is None:
        page = 1
    topic = Topic.query.filter_by(name=name).first_or_404()
    page_data = Weibo.query.join(WeiboRelTopic).filter(    #利用了WeiboRelTopic
            WeiboRelTopic.topic_id==Topic.id,
            Weibo.is_valid==1,
            Topic.id==topic.id
        ).order_by(Weibo.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('home/topic_detail.html',
        topic=topic,
        page_data=page_data,
        form=form)


@app.route('/weibo/comment/<int:pk>/', methods=['GET', 'POST'])
def weibo_comment(pk):
    """ 微博评论 """
    form = WeiboCommentForm()
    weibo = Weibo.query.filter_by(id=pk).first()
    if weibo is None:
        return '404'
    if form.validate_on_submit():
        if current_user.is_authenticated:
            # 执行评论操作
            form.add_comment(weibo, current_user)
        else:
            return '401'
    # 取前条评论数据
    comment_list = Comment.query.filter_by(weibo_id=weibo.id, is_valid=1).limit(5)
    return render_template('moudule/weibo_comments.html',
        form=form,
        weibo=weibo,
        comment_list=comment_list)


@app.route('/user/friend/<nickname>/', methods=['GET', 'POST'])
def user_friend(nickname):
    """ 微博关注 """
    # 查找用户
    to_user = User.query.filter_by(nickname=nickname).first()
    if to_user is None:
        return '404'
    if not current_user.is_authenticated:
        return '401'
    # 查找是否已经关注
    rel = Friend.query.filter_by(from_user_id=current_user.id, to_user_id=to_user.id).first()
    if rel is not None:
        return '402'   # 已经关注
    rel_obj = Friend(
        from_user_id=current_user.id,
        to_user_id=to_user.id,
        created_at=datetime.now()
    )
    db.session.add(rel_obj)
    db.session.commit()
    return '201'



@app.route('/admin/')
@login_required
@staff_perms_required
def admin_index():
    """ 后台管理首页 """
    return render_template('admin/index.html',
        menu_no='index')


@app.route('/admin/user/')
@app.route('/admin/user/page/<int:page>/')
@login_required
#@staff_perms_required
def admin_users(page=None):
    """ 用户管理 """
    if page is None:
        page = 1
    page_data = User.query.filter_by(is_valid=1).paginate(
        page=page, per_page=10)
    return render_template('admin/users.html',
        page_data=page_data,
        menu_no='users')


@app.route('/admin/user/manage/<int:pk>/<int:status>/', methods=['POST'])
def admin_manage_user(pk, status):
    user = User.query.filter_by(id=pk, is_valid=1).first()
    if user is None:
        return '404'
    if not current_user.is_authenticated:
        return '401'

    # 设置用户的状态
    if int(status) == 1:
        user.status = constants.UserStatusEnum.NORMAL
    else :
        user.status = constants.UserStatusEnum.LIMIT
    db.session.add(user)
    db.session.commit()
    return '201'


@app.route('/admin/user/roles/<int:pk>/', methods=['GET', 'POST'])
@login_required
def admin_user_role(pk):
    """ 管理用户的角色 """
    user = User.query.filter_by(id=pk, is_valid=1).first_or_404()
    perms = constants.PermsEnum
    roles = Role.query.filter_by(user_id=user.id, is_valid=1)
    # 已经存在的角色
    has_roles = list(map(lambda n: n.perms.name, roles))
    if request.method == 'POST':
        # 删除所有的角色
        roles.delete()
        # for item in roles:
        #     item.is_valid = 0
        #     db.session.add(item)
        for name in request.form.getlist('perms'):
            enum_perm = getattr(constants.PermsEnum, name, None)
            role_obj = Role(
                user_id=user.id,
                perms=enum_perm,
                name=enum_perm.name,
                )
            db.session.add(role_obj)
        db.session.commit()
        flash('编辑成功')
        return redirect(url_for('admin_user_role', pk=pk))
    return render_template('admin/user_role.html',
        user=user,
        perms=perms,
        has_roles=has_roles,
        menu_no='users')


@app.route('/admin/weibo/')
@app.route('/admin/weibo/page/<int:page>/')
@login_required
@staff_perms_required
def admin_weibos(page=None):
    """ 微博管理 """
    if page is None:
        page = 1
    page_data = Weibo.query.filter_by(is_valid=1).paginate(
        page=page, per_page=3)
    return render_template('admin/weibos.html',
        page_data=page_data,
        menu_no='weibos')


@app.route('/admin/weibo/<int:pk>', methods=['POST'])
@login_required
@staff_perms_required
def admin_weibo_manage(pk):
    """ 管理微博 """
    weibo = Weibo.query.filter_by(id=pk, is_valid=1).first()
    if weibo is None:
        return '404'
    weibo.is_valid = 0
    db.session.add(weibo)
    db.session.commit()
    return '201'
