from flask import Flask, request
from tasks import mongo_tasks

app = Flask(__name__)


@app.route("/")
def index():
    return 'Hello World'


@app.route('/tasks')
def tasks():
    result = mongo_tasks()
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown:
        shutdown()
    return result


if __name__ == '__main__':
    app.run()
