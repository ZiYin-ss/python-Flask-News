from . import passport_blue

from info.utils.captcha.captcha import captcha


@passport_blue.route("/img_code")
def image_code():
    name, text, image_data = captcha.generate_captcha()
    return image_data
