from flask import render_template, current_app, session, jsonify, request, g

from info.models import User, News, Category
from info.modules.index import index_blue
from info.utils.commons import user_login_data
from info.utils.response_code import RET


@index_blue.route('/', methods=["GET", "POST"])
@user_login_data
def show_index():
    # 测试redis存取数据
    # redis_store.set('name', 'zzz')
    # print(redis_store.get('name'))

    # 测试session存取数据
    # session["name"] = "hangman"
    # print(session.get("name"))

    # 没有继承日志之前 使用print输出 不方便控制
    #  print("xxx")

    #  使用日志记录方法loggin进行输出可控  这个和print很像 但是说由log_file这个函数里面的一个对象控制的 详情看那
    # logging.debug("输入调式信息")
    # logging.info("输入详细信息")
    # logging.warning("输入警告信息")
    # logging.error("输入错误信息")

    # 也可以使用current_app来获取输出日志信息 但是这个东西不受上面说的东西控制
    # current_app.logger.debug("输入调式信息2")
    # current_app.logger.info("输入详细信息2")
    # current_app.logger.warning("输入警告信息2")
    # current_app.logger.error("输入错误信息2")

    # user_id = session.get("user_id")  # 1 这个userid就是取出session 给前端 看显示什么
    # #  通过user_id取出对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 2 根据点击量查询前十条新闻
    try:
        #  不要说这个看不懂 就是 先顺序排序 括号里面依据clicks降序排序 后限制条数
        #  SELECT * from info_news ORDER BY clicks DESC LIMIT 10;
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 把news列表里面的一个个元素转成字典 因为查询出来的不就是列表里面一个个的news实例啊
    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 3 查询所有分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    #  将分类对象列表转为字典列表
    category_list = []
    for item in categories:
        category_list.append(item.to_dict())

    #  拼接用户数据 就是这个user_info里面保存的是整个实例字典
    data = {
        "user_info": g.user.to_dict() if g.user else "",
        "news_list": news_list,
        "category_list": category_list
    }

    return render_template("news/index.html", data=data)


# 处理网站logo
#  其实一行这样的代码就可以搞定谢谢<link rel="icon" href="../../static/news/favicon.ico">
#  多会一种也不是问题吗
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')


# 首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page(每页多少条数据)
# 返回值: data数据
@index_blue.route("/newslist")
def newslist():
    # 1. 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "0")
    per_page = request.args.get("per_page", "10")

    # 2. 参数类型转换
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10

    # 3.分页查询
    try:
        #  判断新闻分类是否为1
        if cid == "1":
            #  这个就是分页的语法 前面是查询条件 后面是创建分页 页数和每页多少数据 返回的paginate 有当前页码 总页码 当前页的数据对象 其实不难
            paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
        else:
            paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,
                                                                                                             per_page,
                                                                                                             False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 4. 获取到分页对象中的属性, 总页数, 当前页, 当前页的对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.携带数据, 返回响应
    return jsonify(errno=RET.OK, errmsg="获取新闻成功", totalPage=totalPage, currentPage=currentPage, newsList=news_list)
