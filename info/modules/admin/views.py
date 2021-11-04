from flask import render_template, request, current_app, session, redirect

from . import admin_blue
from ...models import User


@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
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

    return redirect("http://taobao.com")
