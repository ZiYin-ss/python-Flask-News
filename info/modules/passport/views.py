from flask import request

from . import passport_blue

from info.utils.captcha.captcha import captcha
from ... import redis_store
from ...constants import IMAGE_CODE_REDIS_EXPIRES


@passport_blue.route("/image_code")
def image_code():
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    name, text, image_data = captcha.generate_captcha()

    if pre_id:
        redis_store.delete("image_code:%s" % pre_id)

    #  保存到数据库 key value 有效期
    redis_store.set("image_code:%s" % cur_id, text, IMAGE_CODE_REDIS_EXPIRES)

    return image_data
