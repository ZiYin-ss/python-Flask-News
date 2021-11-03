from flask import render_template, g, redirect, request, jsonify

from . import profile_blue
from ... import db
from ...utils.commons import user_login_data
from ...utils.response_code import RET


@profile_blue.route('/user_index')
@user_login_data
def user_index():
    # 如果没有登录是访问不了用户中心的
    if not g.user:
        return redirect("/")

    data = {
        "user_info": g.user.to_dict() if g.user else "",
    }
    return render_template("news/user.html", data=data)


# 获取/设置用户基本信息
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_blue.route("/base_info", methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 1.判断请求方式, 如果是get请求
    if request.method == "GET":
        # 2.携带用户数据, 渲染页面
        return render_template("news/user_base_info.html", user_info=g.user.to_dict())

    # 3.如果是post请求
    # 4.获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 5.校验参数, 为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 6.修改用户的数据
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender
    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")