from flask import render_template, current_app, session

from info.models import User
from info.modules.index import index_blue


@index_blue.route('/', methods=["GET", "POST"])
def index():
    # 测试redis存取数据
    # redis_store.set('name', 'zzz')
    # print(redis_store.get('name'))

    # 测试session存取数据
    # session["name"] = "hangman"
    # print(session.get("name"))

    # 没有继承日志之前 使用print输出 不方便控制
    #  print("xxx")

    #  使用日志记录方法loggin进行输出可控  这个和print很像 但是说由log_file这个函数里面的一个对象控制的 详情看那
    # logging.debug("输入调式信息")
    # logging.info("输入详细信息")
    # logging.warning("输入警告信息")
    # logging.error("输入错误信息")

    # 也可以使用current_app来获取输出日志信息 但是这个东西不受上面说的东西控制
    # current_app.logger.debug("输入调式信息2")
    # current_app.logger.info("输入详细信息2")
    # current_app.logger.warning("输入警告信息2")
    # current_app.logger.error("输入错误信息2")

    user_id = session.get("user_id")
    #  通过user_id取出对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user_info": user.to_dict() if user else ""
    }

    return render_template("news/index.html", data=data)


# 处理网站logo
#  其实一行这样的代码就可以搞定谢谢<link rel="icon" href="../../static/news/favicon.ico">
#  多会一种也不是问题吗
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')
