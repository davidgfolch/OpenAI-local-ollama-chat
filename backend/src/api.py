import re
from functools import reduce
from ast import Dict
from types import NoneType
from flask import Flask, Response, make_response, request
from markdown import markdown
import mdformat
import iaServer
from logConfig import initLog
import logging

app = Flask("api")
# from flask_cors import CORS
# CORS(app)
log = initLog(__file__)

#todo refactor move to mapper
def markDownToHtml(md:str):
    formatted_md = mdformat.text(re.sub(r'\n{3,}', '\n\n',md), options= {'end-of-line':'crlf'})
    return markdown(formatted_md, extensions=['extra']) #https://python-markdown.github.io/extensions/

#todo refactor move to mapper
def listMapper(msg: Dict):
    key = 'a' if 'q' not in msg else 'q'
    value = msg.get(key, '')
    log.info(f"mapping key/value => {key}/{value}")
    return {key: markDownToHtml(value)}


@app.route('/api/v1/chat', methods=['OPTIONS'])
@app.route('/api/v1/chat/delete', methods=['OPTIONS'])
def handle_post_chat():
    # Add CORS allow for this method
    res = make_response()
    corsHeaders(res)
    res.status_code = 200
    return res

def corsHeaders(res: Response):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'DELETE,GET,POST,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return res

def getReqParams(request, params:list): #see https://pypi.org/project/Flask-Parameter-Validation/
    values:list = list(map(lambda param: request.json.get(param), params))
    invalidParams = reduce(lambda a,b: a | b, map(lambda value: isinstance(value,NoneType), values))
    log.info(f"getReqParams -> validParams={invalidParams}")
    if invalidParams: 
        invalidParams = setResponseKO(", ".join(params) + ' are required.')
    values.insert(0, invalidParams)
    return values

def setResponseOK(res):
    return corsHeaders(make_response({'response': res}, 200))

def setResponseKO(errorMsg):
    return corsHeaders(make_response({'error': errorMsg}, 400))

# @app.route('/api/v1/chat', methods=['POST'])
@app.post('/api/v1/chat')
def postMessage():
    errRes, user, question, history, ability = getReqParams(request, ('user', 'question', 'history', 'ability'))
    if isinstance(errRes, Response): return errRes
    return setResponseOK(markDownToHtml(iaServer.ask(user, question, history, ability)))

# @app.route('/api/v1/chat/<string:user>', methods=['GET'])
@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    if not user: return setResponseKO({'error': 'User is required'}, 400)
    msgs = iaServer.list(user)
    msgs = [listMapper(msg) for msg in iaServer.list(user)]
    log.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)

# @app.delete('/api/v1/chat/<string:user>') dont work CORS
@app.get('/api/v1/chat/delete/<string:user>')
def deleteMessages(user):
    if not user: return setResponseKO({'error': 'User is required'}, 400)
    res=iaServer.delete(user)
    return setResponseOK(res)

if __name__ == '__main__':
    app.run(debug=True)
