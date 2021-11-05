from flask import render_template, request, current_app, session, redirect, g, jsonify
import time
from datetime import datetime, timedelta
from . import admin_blue
from ...models import User, News
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


# 用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
def user_list():
    # 1. 获取参数,p
    page = request.args.get("p", "1")

    # 2. 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3. 分页查询用户数据
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_list.html", errmsg="获取用户失败")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "user_list": user_list
    }
    return render_template("admin/user_list.html", data=data)


# 获取/设置新闻审核列表
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: GET, p,keywords
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/news_review')
def news_review():
    # 1. 获取参数,p
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords", "")

    # 2. 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3. 分页查询待审核,未通过的新闻数据
    try:
        # 3.1判断是否有填写搜索关键
        filters = [News.status != 0]
        if keywords:
            #  这个就是模糊查询了 like查询
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 3, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_review.html", errmsg="获取新闻失败")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template("admin/news_review.html", data=data)
