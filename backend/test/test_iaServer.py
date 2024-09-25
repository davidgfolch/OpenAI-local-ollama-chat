import pytest
from unittest.mock import patch
from iaServer import ask, list, get_session_history
from langchain_core.messages import HumanMessage, AIMessage

# Test get session history
def test_get_session_history():
    session = get_session_history("session_1")
    assert session is not None

# Test ask function
@patch('iaServer.with_message_history.invoke')
def test_ask(mock_invoke):
    mock_invoke.return_value = AIMessage(content="Test AI Response")
    response = ask("me", "What is AI?")
    assert response == "Test AI Response"
    mock_invoke.assert_called_once()

# Test list function
@patch('iaServer.get_session_history')
def test_list(mock_get_session_history):
    mock_get_session_history.return_value.messages = [
        HumanMessage(content="What is AI?"),
        AIMessage(content="AI is artificial intelligence.")
    ]
    response = list("me")
    expected_response = [{"q": "What is AI?"}, {"a": "AI is artificial intelligence."}]
    assert response == expected_response
    mock_get_session_history.assert_called_once_with("session_1")
