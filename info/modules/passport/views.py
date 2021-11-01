import json
import re
import random

from flask import request, current_app, make_response, jsonify

from . import passport_blue

from info.utils.captcha.captcha import captcha
from ... import redis_store, constants
from ...constants import IMAGE_CODE_REDIS_EXPIRES

# 获取图片验证码
# 接口文档的写法  请求路径，请求方式，携带参数(参数解释)，返回值
from ...libs.yuntongxun.sms import CCP
from ...utils.response_code import RET


@passport_blue.route("/image_code")
def image_code():
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    name, text, image_data = captcha.generate_captcha()

    try:
        if pre_id:  # 如果有上一次的验证码key 那么把上次的删除 因为验证码这个保存上次的UUID 就是为了去重
            redis_store.delete("image_code:%s" % pre_id)

        #  因为到数据验证的时候 其实也用不到上次的UUID
        #  保存到数据库 key value 有效期
        redis_store.set("image_code:%s" % cur_id, text, IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return "出错了"

    response = make_response(image_data)
    response.headers["Content-Type"] = "image/png"

    return response


# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    #  基本流程
    # 1.获取参数
    # dict_data = json.loads(request.data)
    # mobile = dict_data.get("mobile")
    # image_code = dict_data.get("image_code")
    # image_code_id = dict_data.get("image_code_id")
    #  上面是不是获取手机号 验证码的id 还有就是你输入的验证码的数 不要问这些东西怎么取得 你他妈前端咋学的呢

    # 2.校验参数, 图片验证码
    # redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    # if image_code != redis_image_code:
    #     return jsonify(error=1000, errmsg="验证码输入错误")

    # 3.校验参数, 手机格式
    # re.match 本来就是匹配上了 返回match是true 匹配不上就是none是false
    # if not re.match("1[3-9]\d{9}", mobile):
    #     return jsonify(error=1000, errmsg="手机号格式不匹配")
    #
    # print(mobile)

    # 4.发送短信, 调用封装好的cpp
    # ccp = CCP()
    # result = ccp.send_template_sms(mobile, ['1234', 5], 1)
    #
    # if result == -1:
    #     return jsonify(error=1000, errmsg="短信发送失败")

    # 5.返回发送的状态
    # return jsonify(error=0, errmsg="短信发送成功")

    #  详细流程
    # 1.获取参数
    dict_data = json.loads(request.data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2.参数的为空校验
    if not all([mobile, image_code_id, image_code]):  # 这个语法是这三个只要有一个为空就是false
        return jsonify(error=RET.PARAMERR, errmsg="参数不全")

    # 3.校验手机的格式
    if not re.match("1[3-9]\d{9}", mobile):
        return jsonify(error=RET.DATAERR, errmsg="手机号格式错误")

    # 4.通过图片验证码编号获取, 图片验证码
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DATAERR, errmsg="操作redis失败")

    # 5.判断图片验证码是否过期
    if not redis_image_code:
        return jsonify(error=RET.NODATA, errmsg="图片验证码过期")

    # 6.判断图片验证码是否正确
    if image_code.lower() != redis_image_code.lower():
        return jsonify(error=RET.DATAERR, errmsg="验证码输入错误")

    # 7.删除redis中的图片验证码
    #  其实这一步在这做我真的觉得不算好 但是肯定要做 因为都拿到了验证码 不删验证码干什么呢
    #  或者说可以优化一下 就算这个地方无法删除 也不返回页面 就内部消化
    try:
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DATAERR, errmsg="操作redis失败")

    print(mobile)

    # 8.生成一个随机的短信验证码, 调用ccp发送短信, 判断是否发送成功
    sms = "%06d" % random.randint(0, 99999)  # 不足6位自动补0  这些都是python的基本语法 还有format "{:*^30}".format(s)
    ccp = CCP()
    result = ccp.send_template_sms(mobile, [sms, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)

    if result == -1:
        return jsonify(error=RET.DATAERR, errmsg="短信发送失败")

    # 9.将短信保存到redis中
    try:
        redis_store.set("sms_code:%s" % mobile, sms, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DATAERR, errmsg="图片验证码保存到redis失败")

    # 10.返回响应
    return jsonify(error=RET.OK, errmsg="短信发送成功")
