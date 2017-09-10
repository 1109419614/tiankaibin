#!/usr/bin/python
#coding=utf-8

"""
常用的装饰器
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from functools import wraps
from flask_login import current_user

from flask import abort
from weibo.models import Role
from weibo.constants import PermsEnum


def staff_perms_required(view_func):
	""" 必须是管理员的权限 """

	@wraps(view_func)
	def wrapper(*args, **kwargs):
		role = Role.query.filter_by(
			user_id=current_user.id,
			is_valid=1,
			perms=PermsEnum.ADMIN
			).first()
		if role is None:
			abort(403)
		return view_func(*args, **kwargs)
	return wrapper