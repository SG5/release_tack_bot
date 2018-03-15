import os

from flask import Flask
from tasks import mongo_tasks

app = Flask(__name__)


@app.route("/")
def index():
    return 'Hello World'


@app.route('/tasks')
def tasks():
    return mongo_tasks()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
