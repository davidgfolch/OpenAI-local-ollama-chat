from pathlib import PosixPath
from typing import List
from flask import Flask, request, send_file
import logging
from api import mapper
from api.werkzeugUtil import saveFilesUpload
from constants import UPLOAD_FOLDER
import service.aiService as aiService
from api.flaskUtil import EVENT_STREAM_CHUNKED_HEADERS, setResponseKO, setResponseOK, corsHeaders, getReqParams
from service.langchain.historyExport import exportHistory
from util.files import findFilesRecursive
from util.logUtil import initLog
from model.model import ChatRequest

# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'js', 'py', 'java', 'gif'}

app = Flask("api.api", root_path="/")
log = initLog(__file__, logging.DEBUG)

RES_DELETED_USER_X_HISTORY = "deleted user {0} history {1}"
RES_DELETED_USER_X_HISTORY_INDEX_X = "deleted user {0} history {1} index {2}"
RES_STREAM_CANCELLED_FOR_USER_X = "stream cancelled for user {0}"
OPTIONS = {'provide_automatic_options': False}


@app.errorhandler(Exception)
def handle_error(e: Exception):
    log.error(f"handle_error exception {e}")
    return setResponseKO(e)


@app.route('/<path:uri>', methods=['OPTIONS'])
def cors(uri: str):
    if uri.startswith('api/v1/'):
        log.debug(f"cors for uri={uri} OK")
        res = corsHeaders()
        res.status_code = 200
        return res
    log.debug(f"cors for uri={uri} KO")
    return setResponseKO("Cors not allowed for path")


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
    try:
        preParsedParams = aiService.preParseParams(r)
    except Exception as e:
        return setResponseKO(e)

    def generate():
        for chunk in aiService.sendMessageStream(r, preParsedParams):
            log.debug(f"Received chunk={chunk}")
            yield chunk.content
    return generate(), EVENT_STREAM_CHUNKED_HEADERS


@app.get('/api/v1/chat/<string:user>/<string:history>', **OPTIONS)
def loadHistory(user, history):
    msgs = [mapper.listMapper(m) for m in aiService.loadHistory(user, history)]
    log.info(f"mapped messages {msgs}")
    return setResponseOK(msgs)


# TODO: app.delete('/api/v1/chat/<string:user>') dont work CORS
@app.get('/api/v1/chat/delete/<string:user>/<string:history>', **OPTIONS)
def deleteMessages(user, history):
    aiService.deleteMessages(user, history)
    return setResponseOK(RES_DELETED_USER_X_HISTORY.format(user, history))


@app.get('/api/v1/chat/delete/<string:user>/<string:history>/<int:index>', **OPTIONS)
def deleteMessage(user, history, index):
    log.info(f"api deleteMessage user={user}, history={history} index={index}")
    aiService.deleteMessages(user, history, index)
    return setResponseOK(RES_DELETED_USER_X_HISTORY_INDEX_X.format(user, history, index))


@app.get('/api/v1/chat/cancel/<string:user>', **OPTIONS)
def cancelStreamSignal(user):
    log.info(f"cancelStreamSignal for user {user}")
    aiService.cancelStreamSignal(user)
    return setResponseOK(RES_STREAM_CANCELLED_FOR_USER_X.format(user))


@app.post('/api/v1/files/upload', **OPTIONS)
def filesUpload():
    log.debug(f"filesUpload request.files = {request.files}")
    if request.files:
        fileNames = saveFilesUpload(request)
        if len(fileNames) > 0:
            return setResponseOK(f'File(s) uploaded {fileNames}')
    return setResponseKO('No selected file(s)')


@app.get('/api/v1/files', **OPTIONS)
def getFilesAvailable():
    res: List[PosixPath] = list(
        map(lambda path: str(path).replace(UPLOAD_FOLDER, ''),
            findFilesRecursive(UPLOAD_FOLDER, '*')))
    log.info(f"files = {res}")
    return setResponseOK(res)


@app.get('/api/v1/export/<string:user>/<string:history>', **OPTIONS)
def getExportHistory(user, history):
    file = exportHistory(user, history)
    return corsHeaders(send_file(file, download_name=f'{user}_{history}.zip'))  # as_attachment=True


def run():
    app.run(debug=True)


if __name__ == '__main__':
    run()
