import json
import re

from flask import request, current_app, make_response, jsonify

from . import passport_blue

from info.utils.captcha.captcha import captcha
from ... import redis_store
from ...constants import IMAGE_CODE_REDIS_EXPIRES

# 获取图片验证码
# 接口文档的写法  请求路径，请求方式，携带参数(参数解释)，返回值
from ...libs.yuntongxun.sms import CCP


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
    # 1.获取参数
    dict_data = json.loads(request.data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    #  上面是不是获取手机号 验证码的id 还有就是你输入的验证码的数 不要问这些东西怎么取得 你他妈前端咋学的呢

    # 2.校验参数, 图片验证码
    redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    if image_code != redis_image_code:
        return jsonify(error=1000, errmsg="验证码输入错误")

    # 3.校验参数, 手机格式
    # re.match 本来就是匹配上了 返回match是true 匹配不上就是none是false
    if not re.match("1[3-9]\d{9}", mobile):
        return jsonify(error=1000, errmsg="手机号格式不匹配")

    print(mobile)

    # 4.发送短信, 调用封装好的cpp
    ccp = CCP()
    result = ccp.send_template_sms(mobile, ['1234', 5], 1)

    if result == -1:
        return jsonify(error=1000, errmsg="短信发送失败")

    # 5.返回发送的状态
    return jsonify(error=0, errmsg="短信发送成功")
