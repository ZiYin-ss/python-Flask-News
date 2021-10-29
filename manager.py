"""
相关配置信息
    数据库配置
        为了在项目中用来存储新闻数据以及用户数据的
    redis配置
        缓存访问频率高的内容
        存储session信息 图片验证码 短信验证码之类的
    session配置
    csrf配置
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis

app = Flask(__name__)


class Config(object):
    #  调试信息 是在浏览器显示错误信息还是说错误了直接404
    DEBUG = True

    #  数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123123@localhost:3360/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object("Config")

db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return "helloWorld"


if __name__ == '__main__':
    app.run()
