from flask import render_template, g, redirect, request, jsonify, current_app

from . import profile_blue
from ... import constants
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
