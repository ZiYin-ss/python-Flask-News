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
