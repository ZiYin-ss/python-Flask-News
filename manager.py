from datetime import timedelta, datetime
from random import randint

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


@manager.option('-t', '--test', dest='test')
def add_test_user(test):
    user_list = []

    for i in range(0, 1000):
        user = User()
        user.nick_name = "老王%s" % i
        user.mobile = "138%08d" % i  # 138开头 i写后面 8位 不足用0补
        user.password = "pbkdf2:sha256:150000$NQBQ3b4E$9030d8363d95f83c187f4dd886fba23c1e617ebcf9805dd161e826fc98399e38"
        user.last_login = datetime.now() - timedelta(seconds=randint(0, 3600 * 24 * 31))
        user_list.append(user)

    try:
        #  添加这个列表里面的所有对象到数据库
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "添加数据失败"

    return "添加数据成功"


if __name__ == '__main__':
    manager.run()
