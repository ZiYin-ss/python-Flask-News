from flask import render_template, request, current_app, session, redirect, g
import time
from datetime import datetime, timedelta
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


# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route("/user_count")
@user_login_data
def user_count():
    #  获取用户总数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取总人数失败")

    #  获取月活人数
    localtime = time.localtime()  # 获取当前时间
    # time.struct_time(tm_year=2021, tm_mon=11, tm_mday=5, tm_hour=12, tm_min=27, tm_sec=43, tm_wday=4, tm_yday=309,
    # tm_isdst=0)
    try:
        #  获取本月1号的0点的字符串数据
        month_start_time_str = "%s-%s-01" % (localtime.tm_year, localtime.tm_mon)
        #  根据字符串格式化日期对象
        month_start_time_date = datetime.strptime(month_start_time_str, "%Y-%m-%d")
        month_count = User.query.filter(User.last_login >= month_start_time_date, User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取月活人数失败")

    # 获取日活人数
    try:
        #  获取本日的0点的字符串数据
        #  时分秒不指定 默认是零分零时零秒
        day_start_time_str = "%s-%s-%s" % (localtime.tm_year, localtime.tm_mon, localtime.tm_mday)
        #  根据字符串格式化日期对象
        day_start_time_date = datetime.strptime(day_start_time_str, "%Y-%m-%d")
        day_count = User.query.filter(User.last_login >= day_start_time_date, User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取日活人数失败")

    # 4.获取活跃时间段内,对应的活跃人数
    active_date = []  # 获取活跃的日期
    active_count = []  # 获取活跃的人数
    for i in range(0, 31):
        # 当天开始时间A
        begin_date = day_start_time_date - timedelta(days=i)
        # 当天开始时间, 的后⼀一天B 
        end_date = day_start_time_date - timedelta(days=i - 1)
        # 添加当天开始时间字符串串到, 活跃⽇日期中
        active_date.append(begin_date.strftime("%m-%d"))
        # 查询时间A到B这⼀一天的注册⼈人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                                  User.last_login <= end_date).count()
        # 添加当天注册⼈人数到,获取数量量中
        active_count.append(everyday_active_count)

    active_date.reverse()
    active_count.reverse()

    #  携带数据渲染页面
    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_date": active_date
    }
    return render_template("admin/user_count.html", data=data)
