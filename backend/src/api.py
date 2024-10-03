from flask import Flask, Response, make_response, request
import logging
import iaServer
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
def handle_post_chat():
    # Add CORS allow for this method
    res = make_response()
    flaskUtil.corsHeaders(res)
    res.status_code = 200
    return res


@app.get('/api/v1/models')
def getModels():
    models = iaServer.getModels()
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
            iaServer.sendMessage(model, user, question, history, ability)))


@app.get('/api/v1/chat/<string:user>')
def getMessages(user):
    if not user:
        return flaskUtil.setResponseKO('User is required')
    msgs = iaServer.getMessages(user)
    msgs = [apiMapper.listMapper(msg) for msg in iaServer.getMessages(user)]
    log.info(f"mapped messages {msgs}")
    return flaskUtil.setResponseOK(msgs)

# TODO: @app.delete('/api/v1/chat/<string:user>') dont work CORS


@app.get('/api/v1/chat/delete/<string:user>')
def deleteMessages(user):
    if not user:
        return flaskUtil.setResponseKO('User is required')
    res = iaServer.deleteMessages(user)
    return flaskUtil.setResponseOK(res)


if __name__ == '__main__':
    app.run(debug=True)
