from flask import Flask, Response, request
import logging
from api import mapper
import service.aiService as aiService
from api.flaskUtil import EVENT_STREAM_CHUNKED_HEADERS, setResponseKO, setResponseOK, corsHeaders, getReqParams
from util.logUtil import initLog
from model.model import ChatRequest

app = Flask("api.api", root_path="/")
# from flask_cors import CORS
# CORS(app)
log = initLog(__file__, logging.DEBUG)

RES_DELETED_USER_X_HISTORY = "deleted user {0} history"
RES_DELETED_USER_X_HISTORY_INDEX_X = "deleted user {0} history index {1}"
RES_STREAM_CANCELLED_FOR_USER_X = "stream cancelled for user {0}"


@app.errorhandler(Exception)
def handle_error(e: Exception):
    return setResponseKO(e)


@app.route('/api/v1/chat', methods=['OPTIONS'])
@app.route('/api/v1/chat-stream', methods=['OPTIONS'])
@app.route('/api/v1/models', methods=['OPTIONS'])
@app.route('/api/v1/chat/delete', methods=['OPTIONS'])
@app.route('/api/v1/chat/cancel', methods=['OPTIONS'])
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
            log.debug(f"Received chunk={chunk}")
            yield chunk.content
    return generate(), EVENT_STREAM_CHUNKED_HEADERS


@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    msgs = [mapper.listMapper(msg) for msg in aiService.getMessages(user)]
    log.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)


# TODO: app.delete('/api/v1/chat/<string:user>') dont work CORS
@app.get('/api/v1/chat/delete/<string:user>')
def deleteMessages(user):
    aiService.deleteMessages(user)
    return setResponseOK(RES_DELETED_USER_X_HISTORY.format(user))


@app.get('/api/v1/chat/delete/<string:user>/<int:index>')
def deleteMessage(user, index):
    log.info(f"api deleteMessage user={user}, index={index}")
    aiService.deleteMessages(user, index)
    return setResponseOK(RES_DELETED_USER_X_HISTORY_INDEX_X.format(user, index))


@app.get('/api/v1/chat/cancel/<string:user>')
def cancelStreamSignal(user):
    log.info(f"cancelStreamSignal for user {user}")
    aiService.cancelStreamSignal(user)
    return setResponseOK(RES_STREAM_CANCELLED_FOR_USER_X.format(user))


def run():
    app.run(debug=True)


if __name__ == '__main__':  # TODO: how to test this?
    run()
