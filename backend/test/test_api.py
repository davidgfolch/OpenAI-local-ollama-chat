import pytest
import json
import jsons
from unittest.mock import patch
from api.api import app
from common import generateMsgChunks, mock_chatReq
from service.serviceException import ServiceException


chatReq = jsons.dump(mock_chatReq)


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
            assert {jsonNode: content} == data
        else:  # stream
            assert content == res.data


def assertResponseOK(res, content, asJson=True):
    """ Asserts http status 200 & response.data.response == content """
    assert res.status_code == 200
    if asJson:
        assertData(res, content, 'response')
    else:  # stream
        assertData(res, content)


def assertResponseError(res, content, asJson=True):
    """ Asserts http status 500 & response.data.error == content """
    assert res.status_code == 500
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


def test_getModels(mocker, client):
    expected = ['m1', 'm2']
    mocker.patch("service.aiService.getModels", return_value=expected)
    assertResponseOK(client.get('/api/v1/models'), ['m1', 'm2'])


def test_postMessage(mocker, client):
    mocker.patch("service.aiService.sendMessage",
                 return_value="# test markdown response")
    assertResponseOK(client.post('/api/v1/chat', json=chatReq),
                     '# test markdown response')


def test_postMessage_errRes(mocker, client):
    assertResponseError(client.post('/api/v1/chat', json={}),
                        'Required fields not informed: model, user, question, history, ability')


def test_postMessageStream(mocker, client):
    mocker.patch("service.aiService.sendMessageStream",
                 return_value=generateMsgChunks())
    assertResponseOK(client.post('/api/v1/chat-stream', json=chatReq),
                     b'chunk1chunk2chunk3', asJson=False)


def test_postMessageStream_errRes(mocker, client):
    assertResponseError(client.post('/api/v1/chat-stream', json={}),
                        'Required fields not informed: model, user, question, history, ability')


def test_getMessages(mocker, client):
    mocker.patch("service.aiService.getMessages", return_value=[
                 {'q': 'testQuestion'}, {'a': '# test markdown response'}])
    assertResponseOK(client.get('/api/v1/chat/testUser'),
                     [{'q': 'testQuestion'}, {'a': '# test markdown response'}])


def test_getMessages_validationError(client):
    assertResponseError(client.get('/api/v1/chat'),  # no user param (query path)
                        ["ServiceException: ('Mocked exception', Exception('cause'))",
                         'MethodNotAllowed: 405 Method Not Allowed: The method is not allowed for the requested URL.'])


def test_deleteMessages(mocker, client):
    mocker.patch("service.aiService.deleteMessages", return_value=None)
    assertResponseOK(client.get('/api/v1/chat/delete/testUser'), None)
