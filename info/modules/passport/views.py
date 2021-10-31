from flask import request, current_app, make_response

from . import passport_blue

from info.utils.captcha.captcha import captcha
from ... import redis_store
from ...constants import IMAGE_CODE_REDIS_EXPIRES


# 获取图片验证码
# 接口文档的写法  请求路径，请求方式，携带参数(参数解释)，返回值
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
