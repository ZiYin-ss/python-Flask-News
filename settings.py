class Config(object):
    #  调试信息 是在浏览器显示错误信息还是说错误了直接404
    DEBUG = True

    #  数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123123@localhost:3360/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #  redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
