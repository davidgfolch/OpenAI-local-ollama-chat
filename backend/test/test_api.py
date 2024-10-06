import pytest
import json
from unittest.mock import patch
from api import app
from serviceException import ServiceException


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# helper methods (abstractions)
def assertResponseOK(res, content):
    """ Asserts http status 200 & response.data.response == content """
    assert res.status_code == 200
    if content:
        data = json.loads(res.data)
        assert {'response': content} == data


def assertResponseError(res, content):
    """ Asserts http status 500 & response.data.error == content """
    assert res.status_code == 500
    if content:
        data = json.loads(res.data)
        assert {'error': content} == data


# Test cases
def test_handle_error(client):
    with patch('api.aiServer') as mock:
        mock.getModels.side_effect = ServiceException("Mocked exception", Exception("cause"))
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
    mocker.patch("aiServer.getModels", return_value=expected)
    assertResponseOK(client.get('/api/v1/models'), ['m1', 'm2'])


def test_postMessage_errRes(mocker, client):
    assertResponseError(client.post('/api/v1/chat', json={}),
                        'Required fields not informed: model, user, question, history, ability')


def test_postMessage(mocker, client):
    mocker.patch("aiServer.sendMessage",
                 return_value="# test markdown response")
    assertResponseOK(client.post('/api/v1/chat', json={
        'model': 'testModel',
        'user': 'testUser',
        'question': 'testQuestion',
        'history': 'testHistory',
        'ability': 'testAbility'
    }), '<h1>test markdown response</h1>')


def test_getMessages(mocker, client):
    mocker.patch("aiServer.getMessages", return_value=[
                 {'q': 'testQuestion'}, {'a': '# test markdown response'}])
    assertResponseOK(client.get('/api/v1/chat/testUser'),
                     [{'q': '<p>testQuestion</p>'}, {'a': '<h1>test markdown response</h1>'}])


def test_getMessages_validationError(client):
    assertResponseError(client.get('/api/v1/chat'),  # no user param (query path)
                        ["ServiceException: ('Mocked exception', Exception('cause'))",
                         'MethodNotAllowed: 405 Method Not Allowed: The method is not allowed for the requested URL.'])


def test_deleteMessages(mocker, client):
    mocker.patch("aiServer.deleteMessages", return_value=None)
    assertResponseOK(client.get('/api/v1/chat/delete/testUser'), None)
