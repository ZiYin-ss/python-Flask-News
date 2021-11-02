from flask import render_template, jsonify, current_app, abort, session
from ...models import News, User
from ...utils.response_code import RET
from . import news_blue


# 9.新闻详情展示(新闻)
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户,新闻data字典数据
#  <int:news_id>这个和django一样啊 路由这样写动态类型 对应的视图函数还可以接收到这个news_id
@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    #  根据新闻编号查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 用户id在session中 只要一登录就可以取session 就这个意思 所以和index里面一样的写法
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    #  这个地方是获取前十条热门新闻 因为这个地方 不需要什么 直接就可以获取啊 就点赞最多的呗
    #  多说一句 其实当用户点赞的时候 我们会添加对应的clicks的值 那么这个地方查的时候是不是会更新
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    news_list = []
    for item in click_news:
        news_list.append(item.to_dict())

    # 判断用户是否收藏过该新闻
    is_collect = False
    #  已经登录并且在用户收藏过的新闻列表中
    if user:
        for news in user.collection_news:
            is_collect = True

    if not news:
        abort(404)
    # 如果出错返回404 abort()函数的作用
    # 可以让开发者在检测到web访问错误时，立即将错误信息返回回去，返回的错误码必须是已知http协议中的错误码

    #  携带数据，渲染页面
    data = {
        "news_info": news.to_dict(),
        "news_list": news_list,
        "user_info": user.to_dict() if user else "",
        "is_collected": is_collect
    }
    return render_template("news/detail.html", data=data)
