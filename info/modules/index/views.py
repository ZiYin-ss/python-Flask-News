from info.modules.index import index_blue


@index_blue.route('/', methods=["GET", "POST"])
def hello_world():
    return "helloWorld"
