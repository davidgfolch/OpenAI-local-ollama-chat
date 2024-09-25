import pytest
from flask import json
from api import app, markDownToHtml, listMapper

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test markdown to HTML conversion
def test_markdown_to_html():
    markdown_text = "# Hello World"
    expected_html = "<h1>Hello World</h1>"
    assert markDownToHtml(markdown_text).strip() == expected_html

# Test list mapper function
def test_list_mapper():
    message = {"q": "Hello"}
    expected_output = {"q": "<p>Hello</p>"}
    assert listMapper(message) == expected_output

# Test OPTIONS request on /api/v1/chat
def test_handle_post_chat_options(client):
    res = client.options('/api/v1/chat')
    assert res.status_code == 200
    assert res.headers['Access-Control-Allow-Origin'] == '*'

# Test POST request for chat message with missing fields
def test_post_message_missing_fields(client):
    res = client.post('/api/v1/chat', json={"user": ""})
    assert res.status_code == 400
    assert res.json == {"error": "User and question are required"}

# Test POST request for valid chat message
def test_post_message_valid(client, mocker):
    mocker.patch('iaServer.ask', return_value="Test Response")
    res = client.post('/api/v1/chat', json={"user": "Alice", "question": "What is AI?"})
    assert res.status_code == 200
    assert res.json == {"response": "<p>Test Response</p>"}

# Test GET request for chat messages
def test_get_messages(client, mocker):
    mocker.patch('iaServer.list', return_value=[{"q": "Question?", "a": "Answer"}])
    res = client.get('/api/v1/chat/Alice')
    assert res.status_code == 200
    assert res.json == {"response": [{"q": "<p>Question?</p>", "a": "<p>Answer</p>"}]}
