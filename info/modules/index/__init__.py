from flask import Blueprint

#  创建蓝图对象
index_blue = Blueprint("index_blue", __name__)

#  导入views文件装饰视图函数
#  其实以前就是把views里面的东西放到了这个地方 还是用蓝图装饰视图函数
#  蓝图可以完成Django中的路由问题
from info.modules.index import views
