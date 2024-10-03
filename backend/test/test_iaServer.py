import pytest
from unittest.mock import patch
from iaServer import sendMessage, list, get_session_history
from langchain_core.messages import HumanMessage, AIMessage


def test_get_session_history():
    """Test get session history"""
    session = get_session_history("session_1")
    assert session is not None


@pytest.fixture
def mock_invoke():
    with patch('iaServer.ai') as mock:
        mock.invoke = lambda *args, **kwargs: AIMessage(
            content="Test AI Response")
        yield mock


def test_ask(mock_invoke):
    response = sendMessage("me", "What is AI?")
    assert response == "Test AI Response"
    # mock_invoke.assert_called_once()


@patch('iaServer.get_session_history')
def test_list(mock_get_session_history):
    """Test list function"""
    mock_get_session_history.return_value.messages = [
        HumanMessage(content="What is AI?"),
        AIMessage(content="AI is artificial intelligence.")
    ]
    response = list("me")
    expected_response = [{"q": "What is AI?"}, {
        "a": "AI is artificial intelligence."}]
    assert response == expected_response
    mock_get_session_history.assert_called_once_with("me")
