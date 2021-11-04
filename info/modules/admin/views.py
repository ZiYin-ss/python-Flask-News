from flask import render_template, request, current_app, session, redirect, g

from . import admin_blue
from ...models import User
from ...utils.commons import user_login_data


@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if session.get("is_admin"):
            return redirect("/admin/index")
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不全")

    try:
        admin = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户查询失败")

    if not admin:
        return render_template("admin/login.html", errmsg="用户不存在")

    if not admin.check_passowrd(password):
        return render_template("admin/login.html", errmsg="密码错误")

    session["user_id"] = admin.id
    session["is_admin"] = True

    return redirect("/admin/index")


@admin_blue.route("/index")
@user_login_data
def admin_index():
    data = {
        #  这个g.user 是管理员登录的 那个用户实例 因为是不是更新session了啊 为管理员id
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template("admin/index.html", data=data)
