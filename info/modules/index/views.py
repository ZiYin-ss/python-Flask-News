from info.modules.index import index_blue
from info import redis_store


@index_blue.route('/', methods=["GET", "POST"])
def hello_world():
    redis_store.set('name', 'zzz')
    print(redis_store.get('name'))
    return "helloWorld"
