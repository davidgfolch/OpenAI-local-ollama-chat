from flask import Flask, request
import logging
from api import mapper
import service.aiService as aiService
from api.flaskUtil import EVENT_STREAM_CHUNKED_HEADERS, setResponseKO, setResponseOK, corsHeaders, getReqParams
from util.logUtil import initLog
from model.model import ChatRequest

app = Flask("api.api", root_path="/")
log = initLog(__file__, logging.DEBUG)

RES_DELETED_USER_X_HISTORY = "deleted user {0} history"
RES_DELETED_USER_X_HISTORY_INDEX_X = "deleted user {0} history index {1}"
RES_STREAM_CANCELLED_FOR_USER_X = "stream cancelled for user {0}"
OPTIONS = {'provide_automatic_options': False}


@app.errorhandler(Exception)
def handle_error(e: Exception):
    return setResponseKO(e)


@app.route('/<path:uri>', methods=['OPTIONS'])
def cors(uri: str):
    if uri.startswith('api/v1/'):
        log.debug(f"cors for uri={uri} OK")
        res = corsHeaders()
        res.status_code = 200
        return res
    log.debug(f"cors for uri={uri} KO")
    return setResponseKO()


@app.get('/api/v1/models', **OPTIONS)
def getModels():
    models = aiService.getModels()
    log.info(f"getModels() = {models}")
    return setResponseOK(models)


@app.post('/api/v1/chat', **OPTIONS)
def postMessage():
    r = ChatRequest(*getReqParams(request, ChatRequest.params))
    return setResponseOK(aiService.sendMessage(r))


@app.post('/api/v1/chat-stream', **OPTIONS)
def postMessageStream():
    r = ChatRequest(*getReqParams(request, ChatRequest.params))

    def generate():
        for chunk in aiService.sendMessageStream(r):
            log.debug(f"Received chunk={chunk}")
            yield chunk.content
    return generate(), EVENT_STREAM_CHUNKED_HEADERS


@app.get('/api/v1/chat/<string:user>', **OPTIONS)
def getMessages(user):
    msgs = [mapper.listMapper(m) for m in aiService.getMessages(user)]
    log.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)


# TODO: app.delete('/api/v1/chat/<string:user>') dont work CORS
@app.get('/api/v1/chat/delete/<string:user>', **OPTIONS)
def deleteMessages(user):
    aiService.deleteMessages(user)
    return setResponseOK(RES_DELETED_USER_X_HISTORY.format(user))


@app.get('/api/v1/chat/delete/<string:user>/<int:index>', **OPTIONS)
def deleteMessage(user, index):
    log.info(f"api deleteMessage user={user}, index={index}")
    aiService.deleteMessages(user, index)
    return setResponseOK(RES_DELETED_USER_X_HISTORY_INDEX_X.format(user, index))


@app.get('/api/v1/chat/cancel/<string:user>', **OPTIONS)
def cancelStreamSignal(user):
    log.info(f"cancelStreamSignal for user {user}")
    aiService.cancelStreamSignal(user)
    return setResponseOK(RES_STREAM_CANCELLED_FOR_USER_X.format(user))


def run():
    app.run(debug=True)


if __name__ == '__main__':
    run()
