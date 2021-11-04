from flask import render_template, g, redirect, request, jsonify, current_app

from . import profile_blue
from ... import constants, db
from ...models import News, Category
from ...utils.commons import user_login_data
from ...utils.image_storage import image_storage
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


# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@profile_blue.route("/pic_info", methods=['GET', 'POST'])
@user_login_data
def pic_info():
    # 1.判断请求方式, 如果是get请求
    if request.method == "GET":
        return render_template("news/user_pic_info.html", user_info=g.user.to_dict())
    # 2.携带用户的数据, 渲染页面
    avatar = request.files.get("avatar")

    # 3.如果是post请求
    if not all([avatar]):
        return jsonify(errno=RET.PARAMERR, errmsg="图片不能为空")

    # print(avatar)  <FileStorage: '0.jpg' ('image/jpeg')>
    # 6. 上传图像, 判断图片是否上传成功
    try:
        #  前端是传过来的文件 二进制读取就用read()就可以了 这样 avatar就是一个二进制文件了
        image_name = image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)

    # 7.将图片设置到用户对象
    if image_name:
        g.user.avatar_url = image_name
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="上传失败")

    # 8.返回响应
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX + image_name
    }

    return jsonify(errno=RET.OK, errmsg="上传成功", data=data)


# 获取/设置用户密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_blue.route("/pass_info", methods=['GET', 'POST'])
@user_login_data
def pass_info():
    #   1. 判断请求方式,如果是get请求
    #   2. 直接渲染页面
    if request.method == "GET":
        return render_template("news/user_pass_info.html", user_info=g.user.to_dict())

    #   3. 如果是post请求,获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    #   4. 校验参数,为空校验
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    #   5. 判断老密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")

    #   6. 设置新密码
    g.user.password = new_password

    #   7. 返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 获取新闻收藏列表
# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@profile_blue.route('/collection')
@user_login_data
def collection():
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    try:
        #  这个是模型类的查询方式 就是多对多关系  找到当前用户对应的收藏 按照他们的创建实际倒序排列
        #  多说一句这个地方是查询用户收藏的新闻对象 这个paginate返回的是news实例
        paginate = g.user.collection_news.order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }

    return render_template("news/user_collection.html", data=data)


# 获取/设置,新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据, POST,errno,errmsg
@profile_blue.route("/news_release", methods=['GET', 'POST'])
@user_login_data
def news_release():
    if request.method == "GET":
        # 携带分类数据渲染页面  就是有个地方展示分类类别的
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取分类失败")
        category_list = []
        for categorie in categories:
            category_list.append(categorie.to_dict())
        return render_template("news/user_news_release.html", categories=category_list)

    # 3.如果是POST, 获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    # 4.校验参数, 为空校验
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 5.上传图片, 判断是否上传成功
    try:
        # 读取图片为二进制 上传
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="图片上传失败")

    # 6.创建新闻对象, 设置属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1

    # 7.保存到数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻发布失败")

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="图片发布成功")


# 用户新闻列表
# 请求路径: /user/news_list
# 请求方式:GET
# 请求参数:p
# 返回值:GET渲染user_news_list.html页面
@profile_blue.route("/news_list", methods=['GET'])
@user_login_data
def news_list():
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page, 10,
                                                                                                           False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }

    return render_template("news/user_news_list.html", data=data)


# 获取我的关注
# 请求路径: /user/user_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面,字典data数据
@profile_blue.route('/user_follow', methods=['GET'])
@user_login_data
def user_follow():
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    try:
        #  这个地方是反向查询 就是followers是自己的粉丝 就是说别人关注你了
        #  而followed是查询你关注了谁 通过第三张表查的 就是根据自己的id查询我关注了谁
        #  查询的还是user实例
        paginate = g.user.followed.paginate(page, 4, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    author_list = []
    for author in items:
        author_list.append(author.to_dict())

    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "author_list": author_list
    }

    return render_template("news/user_follow.html", data=data)
