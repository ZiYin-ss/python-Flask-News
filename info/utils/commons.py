# 自定义过滤器 实现热门新闻的颜色过滤
from flask import session, current_app, g
from functools import wraps


def hot_news_filter(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        g.user = user

        return view_func(*args, **kwargs)

    return wrapper

