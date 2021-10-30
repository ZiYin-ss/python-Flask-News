from datetime import timedelta

from redis import StrictRedis


class Config(object):
    #  调试信息 是在浏览器显示错误信息还是说错误了直接404
    DEBUG = True
    SECRET_KEY = "FSDFSDFSDFSD"
    #  数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123123@localhost:3360/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #  redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #  session配置信息  再这配置 Session(app)就可以了
    SESSION_TYPE = "redis"  # 设置session# 存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)  # 设置session有效期
    SESSION_USE_SIGNER = True  # 设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)   # 有效期两天
