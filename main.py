import os
from sanic import response

from tasks.new_software import mongo_tasks
from tasks.ru_block import generate_ipset
from tasks.visa_bulletin import VisaBulletin
from init import app


@app.get("/")
async def index(_):
    return response.text('Hello World')


@app.get("/favicon.ico")
async def index(_):
    return response.text('', 404)


@app.get('/tasks')
async def tasks(_):
    await mongo_tasks()
    return response.text('ok')


@app.get('/vb')
async def tasks(_):
    await VisaBulletin().run()
    return response.text('ok')


@app.get('/ru-block')
async def tasks(_):
    return response.stream(generate_ipset)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
