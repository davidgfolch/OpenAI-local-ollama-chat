import io
import pytest
import json
import jsons
from unittest.mock import patch
from api.api import RES_DELETED_USER_X_HISTORY, RES_DELETED_USER_X_HISTORY_INDEX_X, RES_STREAM_CANCELLED_FOR_USER_X, app
from api.flaskUtil import REQUIRED_FIELDS
from tests.common import HISTORY, USER, mockMsgChunks, CHAT_REQUEST
from service.serviceException import ServiceException

VALIDATION_ERR_MSG = [f'ValidationException: {
    REQUIRED_FIELDS}model, user, temperature, question, history, ability']

chatReq = jsons.dump(CHAT_REQUEST)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# helper methods (abstractions)
def assertData(res, content, jsonNode=None):
    if content:
        if jsonNode:
            data = json.loads(res.data)
            assert data == {jsonNode: content}
        else:  # stream
            assert res.data == content


def assertResponseOK(res, content, asJson=True):
    """ Asserts http status 200 & response.data.response == content """
    assert res.status_code == 200
    if asJson:
        assertData(res, content, 'response')
    else:  # stream
        assertData(res, content)


def assertResponseError(res, content, asJson=True):
    """ Asserts http status 400/500 & response.data.error == content """
    assert res.status_code == 500 or 400
    if asJson:
        assertData(res, content, 'error')
    else:  # stream
        assertData(res, content)


# Test cases
def test_handle_error(client):
    with patch('service.aiService.getModels') as mock:
        mock.side_effect = ServiceException(
            "Mocked exception", Exception("cause"))
        res = client.get('/api/v1/models')
        assertResponseError(
            res, ["ServiceException: ('Mocked exception', Exception('cause'))"])


def test_cors(client):
    res = client.options('/api/v1/chat')
    assert res.headers['Access-Control-Allow-Origin'] == '*'
    assert res.headers['Access-Control-Allow-Methods'] == 'DELETE,GET,POST,OPTIONS'
    assert res.headers['Access-Control-Allow-Headers'] == 'Content-Type'
    assertResponseOK(res, None)
    res = client.options('/api/X-v1/chat')
    assertResponseError(res, ['Cors not allowed for path'])


def test_getModels(mocker, client):
    expected = ['m1', 'm2']
    mocker.patch("service.aiService.getModels", return_value=expected)
    assertResponseOK(client.get('/api/v1/models'), expected)


def test_postMessage(mocker, client):
    mocker.patch("service.aiService.sendMessage",
                 return_value="# test markdown response")
    assertResponseOK(client.post('/api/v1/chat', json=chatReq),
                     '# test markdown response')


def test_postMessage_errRes(mocker, client):
    res = client.post('/api/v1/chat', json={})
    assertResponseError(res, VALIDATION_ERR_MSG)


def test_postMessageStream(mocker, client):
    mocker.patch("service.aiService.sendMessageStream",
                 return_value=mockMsgChunks(3))
    assertResponseOK(client.post('/api/v1/chat-stream',
                     json=chatReq), b'chunk1chunk2chunk3', asJson=False)


def test_postMessageStream_exception(client):
    with patch("service.aiService.preParseParams") as mock:
        mock.side_effect = ServiceException('test')
        assertResponseError(client.post('/api/v1/chat-stream', json=chatReq),
                            VALIDATION_ERR_MSG.append('ServiceException: test'))


@pytest.mark.parametrize('user,history', [['', ''], [USER, HISTORY]])
def test_getMessages(mocker, client, user, history):
    if not user == '':
        mocker.patch("service.aiService.getMessages", return_value=[
            {'q': 'testQuestion'}, {'a': '# test markdown response'}])
    res = client.get(f'/api/v1/chat/{user}/{history}')
    if user == '':
        assertResponseError(res,  # no params (query path)
                            ['MethodNotAllowed: 405 Method Not Allowed: The method is not allowed for the requested URL.'])
    else:
        assertResponseOK(res, [{'q': 'testQuestion'}, {
                         'a': '# test markdown response', 'id': '', 'metadata': ''}])


def test_deleteMessages(mocker, client):
    mocker.patch("service.aiService.deleteMessages", return_value=None)
    assertResponseOK(client.get(f'/api/v1/chat/delete/{USER}/{HISTORY}'),
                     RES_DELETED_USER_X_HISTORY.format(USER, HISTORY))


def test_deleteMessage(mocker, client):
    mocker.patch("service.aiService.deleteMessages", return_value=None)
    assertResponseOK(client.get(f'/api/v1/chat/delete/{USER}/{HISTORY}/1'),
                     RES_DELETED_USER_X_HISTORY_INDEX_X.format(USER, HISTORY, 1))


def test_cancelStreamSignal(mocker, client):
    mocker.patch("service.aiService.cancelStreamSignal", return_value=None)
    assertResponseOK(client.get(f'/api/v1/chat/cancel/{USER}'),
                     RES_STREAM_CANCELLED_FOR_USER_X.format(USER))


@pytest.mark.parametrize('fileNames', [[], ['test.py']])
def test_uploadFiles(mocker, client, fileNames):
    mocker.patch("api.werkzeugUtil.saveFilesUpload", return_value=fileNames)
    data = {'file': (io.BytesIO(b"abcdef"), file) for file in fileNames}
    res = client.post('/api/v1/files/upload', data=data,
                      content_type='multipart/form-data')
    if len(fileNames) == 0:
        assertResponseError(res, ['No selected file(s)'])
    else:
        assertResponseOK(res, f'File(s) uploaded {fileNames}')


def test_getFilesAvailable(client):
    with patch('util.files.findFilesRecursive') as mock:
        mock.return_value = []
        assertResponseOK(client.get('/api/v1/files'), [])
