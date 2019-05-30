import os
from sanic import response

from tasks.new_software import mongo_tasks
from tasks.ru_block import generate_ipset
from tasks.visa_bulletin import VisaBulletin
from init import app


@app.route("/")
async def index(_):
    return response.text('Hello World')


@app.route("/favicon.ico")
async def index(_):
    return response.text('', 404)


@app.route('/tasks')
async def tasks(_):
    await mongo_tasks()
    return response.text('ok')


@app.route('/vb')
async def tasks(_):
    await VisaBulletin().run()
    return response.text('ok')


@app.route('/ru-block')
async def tasks(_):
    return response.stream(generate_ipset)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
