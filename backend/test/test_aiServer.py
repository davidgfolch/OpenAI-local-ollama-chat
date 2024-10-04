import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from aiServer import getModels, sendMessage, getMessages, deleteMessages

# Define fixtures for testing


@pytest.fixture
def mock_openaiUtil():
    with patch('aiServer.openaiUtil') as mock:
        yield mock


@pytest.fixture
def mock_hostArgs():
    with patch('aiServer.hostArgs', {'base_url': 'http://test-api'}):
        yield

# Test cases


def test_getModels(mock_openaiUtil, mock_hostArgs):
    mock_openaiUtil.getModels.return_value = ['model1', 'model2']
    models = getModels()
    assert models == ['model1', 'model2']
    mock_openaiUtil.getModels.assert_called_once()


@pytest.mark.parametrize("model, user, question, history, ability", [
    ('testModel', 'testUser', 'testQuestion', "history1", "Ingeniería de software")
])
def test_sendMessage(model, user, question, history, ability):
    with patch('aiServer.with_model') as mock_with_model:
        mock_response = MagicMock()
        mock_response.content = "testResponse"
        mock_with_model.return_value.invoke.return_value = mock_response
        response = sendMessage(model, user, question, history, ability)
        assert response == "testResponse"
        mock_with_model.assert_called_once_with(model)
        mock_with_model.return_value.invoke.assert_called_once_with(
            input={"history": history, "ability": ability, "input": question},
            config={"configurable": {"session_id": user, "model": model}})


def test_getMessages():
    with patch('aiServer.get_session_history') as mock_get_session_history:
        msgs = [HumanMessage("question"), AIMessage("answer")]
        mock_get_session_history.return_value.messages = msgs
        messages = getMessages('testUser')
        assert messages == [{'q': 'question'}, {'a': 'answer'}]
        mock_get_session_history.assert_called_once_with('testUser')


def test_deleteMessages():
    with patch('aiServer.get_session_history') as mock_get_session_history:
        mock_get_session_history().clear = MagicMock()
        deleteMessages('testUser')
        mock_get_session_history.return_value.clear.assert_called_once()