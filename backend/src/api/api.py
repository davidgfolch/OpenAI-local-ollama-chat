from flask import Flask, Response, request
import logging
from api import mapper
import service.aiService as aiService
from api.flaskUtil import EVENT_STREAM_CHUNKED_HEADERS, setResponseKO, setResponseOK, corsHeaders, getReqParams
from util.logUtil import initLog
from model.model import ChatRequest

app = Flask("api", root_path="/")
# from flask_cors import CORS
# CORS(app)
log = initLog(__file__, logging.DEBUG)


@app.errorhandler(Exception)
def handle_error(e: Exception):
    return setResponseKO(e)


@app.route('/api/v1/chat', methods=['OPTIONS'])
@app.route('/api/v1/chat-stream', methods=['OPTIONS'])
@app.route('/api/v1/models', methods=['OPTIONS'])
@app.route('/api/v1/chat/delete', methods=['OPTIONS'])
def cors():
    # Add CORS allow for this method
    res = corsHeaders()
    res.status_code = 200
    return res


@app.get('/api/v1/models')
def getModels():
    models = aiService.getModels()
    log.info(f"getModels() = {models}")
    return setResponseOK(models)


@app.post('/api/v1/chat')
def postMessage():
    params = getReqParams(request, ChatRequest.params)
    req = ChatRequest(*params)
    if isinstance(req.errRes, Response):
        return req.errRes
    return setResponseOK(aiService.sendMessage(req))


@app.post('/api/v1/chat-stream')
def postMessageStream():
    params = getReqParams(request, ChatRequest.params)
    req = ChatRequest(*params)
    if isinstance(req.errRes, Response):
        return req.errRes

    def generate():
        for chunk in aiService.sendMessageStream(req):
            log.info(f"Received chunk={chunk}")
            yield chunk.content
    return generate(), EVENT_STREAM_CHUNKED_HEADERS


@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    msgs = aiService.getMessages(user)
    msgs = [mapper.listMapper(msg) for msg in aiService.getMessages(user)]
    log.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)


# TODO: app.delete('/api/v1/chat/<string:user>') dont work CORS
@app.get('/api/v1/chat/delete/<string:user>')
def deleteMessages(user):
    res = aiService.deleteMessages(user)
    return setResponseOK(res)


def run():
    app.run(debug=True)


if __name__ == '__main__':  # TODO: how to test this?
    run()
