#!/usr/bin/python
#coding=utf-8

from app import create_app,db,login_manager
from app.models import Comments,User,Role,Weibo,Friends,Topic,topic_weibo
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app=create_app('default')
manager=Manager(app)
migrate=Migrate(app,db)

@manager.shell
def make_shell_context():
    return dict(app=app,db=db,login_manager=login_manager,User=User,Comments=Comments,Role=Role,Weibo=Weibo,Friends=Friends,Topic=Topic,topic_weibo=topic_weibo)
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()
