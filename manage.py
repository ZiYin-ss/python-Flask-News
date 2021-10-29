"""
相关配置信息
    数据库配置
        为了在项目中用来存储新闻数据以及用户数据的
    redis配置
        缓存访问频率高的内容
        存储session信息 图片验证码 短信验证码之类的
    session配置
        保存用户登录信息
    csrf配置
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from settings import Config
from flask_session import Session

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
#  decode_responses 自解码
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


@app.route('/')
def hello_world():
    return "helloWorld"


if __name__ == '__main__':
    app.run()
