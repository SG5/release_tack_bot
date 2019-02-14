import os
from sanic import response

from tasks import mongo_tasks
from init import app


@app.route("/")
async def index(request):
    return response.text('Hello World')


@app.route('/tasks')
async def tasks(request):
    await mongo_tasks()
    return response.text('ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
