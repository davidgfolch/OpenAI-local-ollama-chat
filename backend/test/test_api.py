import pytest
from api import app
from apiMapper import markDownToHtml, listMapper


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_markdown_to_html():
    """Test markdown to HTML conversion"""
    markdown_text = "# Hello World"
    expected_html = "<h1>Hello World</h1>"
    assert markDownToHtml(markdown_text).strip() == expected_html


def test_list_mapper():
    """Test list mapper function"""
    message = {"q": "Hello"}
    expected_output = {"q": "<p>Hello</p>"}
    assert listMapper(message) == expected_output


def test_handle_post_chat_options(client):
    """Test OPTIONS request on /api/v1/chat"""
    res = client.options('/api/v1/chat')
    assert res.status_code == 200
    assert res.headers['Access-Control-Allow-Origin'] == '*'


def test_post_message_missing_fields(client):
    """Test POST request for chat message with missing fields"""
    res = client.post('/api/v1/chat', json={"user": ""})
    assert res.status_code == 500
    assert res.json == {
        "error": 'Required fields not informed: question, history, ability'}


def test_post_message_valid(client, mocker):
    """Test POST request for valid chat message"""
    mocker.patch('iaServer.ask', return_value="Test Response")
    res = client.post('/api/v1/chat', json={"user": "me", "question": "What is AI?",
                                            "history": "myHistory",
                                            "ability": "Ingeniería de software"})
    assert res.status_code == 200
    assert res.json == {"response": "<p>Test Response</p>"}


def test_get_messages(client, mocker):
    """Test GET request for chat messages"""
    mocker.patch('iaServer.list', return_value=[
        {'q': 'Hola, soy humano!'}, {'a': 'Hola soy IA.'}])
    res = client.get('/api/v1/chat/me')
    assert res.status_code == 200
    assert res.json == {"response": [
        {'q': '<p>Hola, soy humano!</p>'}, {'a': '<p>Hola soy IA.</p>'}]}
