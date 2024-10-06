from flask import Flask, Response, request
import logging
import aiServer
import apiMapper
import flaskUtil
from logConfig import initLog

app = Flask("api")
# from flask_cors import CORS
# CORS(app)
log = initLog(__file__, logging.DEBUG)


@app.errorhandler(Exception)
def handle_error(e: Exception):
    return flaskUtil.setResponseKO(e)


@app.route('/api/v1/chat', methods=['OPTIONS'])
@app.route('/api/v1/models', methods=['OPTIONS'])
@app.route('/api/v1/chat/delete', methods=['OPTIONS'])
def cors():
    # Add CORS allow for this method
    res = flaskUtil.corsHeaders()
    res.status_code = 200
    return res


@app.get('/api/v1/models')
def getModels():
    models = aiServer.getModels()
    log.info(f"getModels() = {models}")
    return flaskUtil.setResponseOK(models)


@app.post('/api/v1/chat')
def postMessage():
    (errRes, model, user, question, history, ability) = flaskUtil.getReqParams(
        request, ['model', 'user', 'question', 'history', 'ability'])
    if isinstance(errRes, Response):
        return errRes
    return flaskUtil.setResponseOK(
        apiMapper.markDownToHtml(
            aiServer.sendMessage(model, user, question, history, ability)))


@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    msgs = aiServer.getMessages(user)
    msgs = [apiMapper.listMapper(msg) for msg in aiServer.getMessages(user)]
    log.info(f"mapped messages {msgs}")
    return flaskUtil.setResponseOK(msgs)


@app.get('/api/v1/chat/delete/<string:user>')  # TODO: app.delete('/api/v1/chat/<string:user>') dont work CORS
def deleteMessages(user):
    res = aiServer.deleteMessages(user)
    return flaskUtil.setResponseOK(res)


if __name__ == '__main__':  # TODO: how to test this?
    app.run(debug=True)
