from ast import Dict
from venv import logger
from flask import Flask, Response, make_response, request
from markdown import markdown
import iaServer

app = Flask(__name__)

#todo refactor move to mapper
def markDownToHtml(mkdwn):
    return markdown(mkdwn, extensions=['fenced_code'])

#todo refactor move to mapper
def listMapper(msg: Dict):
    key = 'a' if 'q' not in msg else 'q'
    value = msg.get(key, '')
    logger.info(f"mapping key/value => {key}/{value}")
    return {key: markDownToHtml(value)}


@app.route('/api/v1/chat', methods=['OPTIONS'])
def handle_post_chat():
    # Add CORS allow for this method
    res = make_response()
    corsHeaders(res)
    res.status_code = 200
    return res

def corsHeaders(res: Response):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return res

def setResponseOK(res):
    return corsHeaders(make_response({'response': res}, 200))

def setResponseKO(errorMsg):
    return corsHeaders(make_response({'error': errorMsg}, 400))

# @app.route('/api/v1/chat', methods=['POST'])
@app.post('/api/v1/chat')
def postMessage():
    #todo: simplify model & validation with json.loads(request.data) ??? -> from flask import Flask, request, json
    user = request.json.get('user')
    question = request.json.get('question')
    if not user or not question: return setResponseKO('User and question are required')
    return setResponseOK(markDownToHtml(iaServer.ask(user = user, question = question)))

# @app.route('/api/v1/chat/<string:user>', methods=['GET'])
@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    if not user: return setResponseKO({'error': 'User is required'}, 400)
    msgs = iaServer.list(user)
    msgs = [listMapper(msg) for msg in iaServer.list(user)]
    logger.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)

if __name__ == '__main__':
    app.run(debug=True)
