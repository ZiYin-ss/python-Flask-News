from flask import Blueprint, request, session, redirect

admin_blue = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


# 使用请求钩子 拦截普通用户的请求
#  拦截普通用户  拦截的是访问了非登录页面
#  只有访问了admin_blue所装饰的视图函数需要拦截
@admin_blue.before_request
def before_request():
    if request.url.endswith("/admin/login"):
        #  别想太简单了 登录了才有is_admin 别人登录你也拦截 你做个人啊
        pass
    else:
        if session.get("is_admin"):
            pass
        else:
            #  注意这个请求前 你如果拦截的话 用return 不会走视图函数了
            #  假如你要让他走的话 就什么都不写 就会自己走下去
            return redirect('/admin/login')
