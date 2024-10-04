import pytest
import json
from api import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def assertResponseOK(response, content):
    assert response.status_code == 200
    data = json.loads(response.data)
    assert {'response': content} == data


# Test cases
def test_getModels(mocker, client):
    expected = ['m1', 'm2']
    mocker.patch("aiServer.getModels", return_value=expected)
    assertResponseOK(client.get('/api/v1/models'), ['m1', 'm2'])


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
    mocker.patch("aiServer.getMessages", return_value=[{'q': 'testQuestion'}, {'a': '# test markdown response'}])
    assertResponseOK(client.get('/api/v1/chat/testUser'),
                     [{'q': '<p>testQuestion</p>'}, {'a': '<h1>test markdown response</h1>'}])


def test_deleteMessages(mocker, client):
    mocker.patch("aiServer.deleteMessages", return_value=None)
    assertResponseOK(client.get('/api/v1/chat/delete/testUser'), None)
