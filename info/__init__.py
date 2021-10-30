import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import config_dict

#  定义全局变量
redis_store = None


#  这个就是工厂方法
#  注册配置信息
def create_app(config_name):
    app = Flask(__name__)

    #  加载配置类
    config = config_dict.get(config_name)
    app.config.from_object(config)

    # 调用日志方法 记录软件运行信息
    log_file(config.LEVEL_NAME)

    #  创建SQLAlchemy对象 关联app
    db = SQLAlchemy(app)

    #  decode_responses自解码  配置redis连接  创建redis对象
    global redis_store  # 将局部变量声明为一个全局的 语法是这样的 不是直接在下面的redis_store 前面加个global的
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    #  创建session对象 读取App中的session配置信息  配置session在config文件中 都是key-value类型
    Session(app)

    #  使用CSRFProtect保护app  验证csrf信息才能对后端进行操作
    CSRFProtect(app)

    # 将首页蓝图注册到app中
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    return app


def log_file(level_name):
    # 设置日志的记录等级
    # DEBUG = 10  INFO = 20 WARNING = 30 ERROR = 40
    # 调试debug级 一旦设置级别大于等于该级别的信息全部都会输出
    logging.basicConfig(level=level_name)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限  如果超过了 就把前面的删掉 把新的东西放到后面
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
