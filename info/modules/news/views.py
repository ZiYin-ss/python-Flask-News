from flask import render_template, jsonify, current_app, abort, session, g, request

from ... import db
from ...models import News, User, Comment
from ...utils.commons import user_login_data
from ...utils.response_code import RET
from . import news_blue


# 新闻详情展示(新闻)
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
        if news in user.collection_news:
            is_collect = True

    # 查询数据库中该新闻的所有评论内容
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    comments_list = []
    for comment in comments:
        comments_list.append(comment.to_dict())

    if not news:
        abort(404)
    # 如果出错返回404 abort()函数的作用
    # 可以让开发者在检测到web访问错误时，立即将错误信息返回回去，返回的错误码必须是已知http协议中的错误码

    #  携带数据，渲染页面
    data = {
        "news_info": news.to_dict(),
        "news_list": news_list,
        "user_info": user.to_dict() if user else "",
        "is_collected": is_collect,
        "comments": comments_list
    }
    return render_template("news/detail.html", data=data)


# 收藏功能接口
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数:news_id,action, g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 1. 判断用户是否登陆了
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2. 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 3. 参数校验,为空校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4. 操作类型校验
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 5. 根据新闻的编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 6. 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 7. 根据操作类型,进行收藏&取消收藏操作
    if action == "collect":
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        if news in g.user.collection_news:
            #  移除特定的数据 这个其实说到底也是对数据库的操作 但是自动提交了
            g.user.collection_news.remove(news)

    # 8. 返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 新闻评论后端
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数:news_id,comment,parent_id, g.user
# 返回值: errno,errmsg,评论字典
@news_blue.route("/news_comment", methods=['POST'])
@user_login_data
def news_comment():
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 创建评论对象 设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:  # 这个父id其实就相当于我们在别人的评论下面评论 这个父ID其实也是一条评论 就这
        comment.parent_id = parent_id

    # 将上面的评论对象保存到数据库 其实这个地方也是多对多关系 评论 还要显示的呢
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论失败")

    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())
