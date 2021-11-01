from datetime import timedelta
from redis import StrictRedis
import logging


#  基类配置
class Config(object):
    #  调试信息 是在浏览器显示错误信息还是说错误了直接404
    DEBUG = True
    SECRET_KEY = "FSDFSDFSDFSD"

    #  数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123123@127.0.0.1:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 自动提交

    #  redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #  session配置信息  再这配置 Session(app)就可以了
    SESSION_TYPE = "redis"  # 设置session# 存储类型
    # decode_responses = True 这个不能加上自解码 因为本来就不需要 底层做好了
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置session有效期
    SESSION_USE_SIGNER = True  # 设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)  # 有效期两天

    #  默认日志级别
    LEVEL_NAME = logging.DEBUG


# 开发环境配置信息
class DevelopConfig(Config):
    pass


# 生产(上线)环境配置信息
class ProductConfig(Config):
    LEVEL_NAME = logging.ERROR
    DEBUG = False


# 测试环境配置信息
class TestConfig(Config):
    pass


#  提供一个统一的访问入口
#  还可以这样的 app.config.from_object("settings.DevelopmentConfig")
config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestConfig
}
