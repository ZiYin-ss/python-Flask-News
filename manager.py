from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import create_app, db, models
from info.models import User

app = create_app("develop")

#  创建manager对象管理app
manager = Manager(app)

# 使用migrate关联app db
Migrate(app, db)

# 给manager添加一条操作命令
manager.add_command('db', MigrateCommand)


#  定义方法添加管理员对象 主要是前面添加俩个这个就代表是一个脚本了 可以在终端中运行
#  给manager添加一个脚本运行方法
#  参数一是参数名称 参数二是对参数一的解释 参数三目的参数就是用来传递给形式参数调用的
#  也就是说参数一传递之后 给了目标参数
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_superuser(username, password):
    admin = User()
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True
    try:
        db.session.add(admin)
    except Exception as e:
        current_app.logger.error(e)
        return "创建失败"
    return "创建成功"


if __name__ == '__main__':

    manager.run()
