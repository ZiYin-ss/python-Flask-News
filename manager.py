from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from settings import Config
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

#  注册配置信息
app.config.from_object(Config)
#  配置mysql
db = SQLAlchemy(app)
#  decode_responses 自解码  配置redis连接
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
#  创建session对象 读取App中的session配置信息  配置session在setting文件中 都是key-value类型
Session(app)
#  使用CSRFProtect保护app  验证csrf信息才能对后端进行操作
CSRFProtect(app)


@app.route('/')
def hello_world():

    return "helloWorld"


if __name__ == '__main__':
    app.run()
