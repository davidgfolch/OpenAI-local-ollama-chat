import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from tests.common import CHAT_REQUEST, USER, createMsgChunk, generateMsgChunks
from service import aiService


# Define fixtures for testing
@pytest.fixture
def mock_openaiUtil():
    with patch('service.aiService.openaiUtil') as mock:
        yield mock


# Test cases
def test_getModels_exception(mock_openaiUtil):
    mock_openaiUtil.getModels.side_effect = Exception("Mocked exception")
    with pytest.raises(Exception) as ex_res:
        aiService.getModels()
    assert str(ex_res.value) == aiService.ERROR_OPENAI_GET_AVAILABLE_MODELS


def test_getModels(mock_openaiUtil):
    mock_openaiUtil.getModels.return_value = ['model1', 'model2']
    models = aiService.getModels()
    assert models == ['model1', 'model2']
    mock_openaiUtil.getModels.assert_called_once()


def test_sendMessage():
    with patch('service.aiService.invoke') as mock_invoke:
        mock_res = MagicMock()
        mock_res.content = "testResponse"
        mock_invoke.return_value = mock_res
        res = aiService.sendMessage(CHAT_REQUEST)
        assert res == "testResponse"
        mock_invoke.assert_called_once_with(CHAT_REQUEST)


def test_sendMessage_exception():
    with patch('service.aiService.invoke') as mock_invoke:
        mock_invoke.side_effect = Exception("Mocked exception")
        with pytest.raises(Exception) as ex_res:
            aiService.sendMessage(CHAT_REQUEST)
        assert str(ex_res.value) == aiService.ERROR_LANGCHAIN_SEND_CHAT_MESSAGE


def test_sendMessageStream():
    with patch('service.aiService.stream') as mock_stream:
        mock_stream.return_value = generateMsgChunks()
        generator = aiService.sendMessageStream(CHAT_REQUEST)
        chunks = list(generator)
        for x in range(1, 4):
            assert chunks[x-1] == createMsgChunk(content=f"chunk{x}")


def test_sendMessageStream_cancel():
    aiService.cancelStreamSignal(CHAT_REQUEST.user)
    with patch('service.aiService.stream') as mock_stream:
        mock_stream.return_value = generateMsgChunks()
        generator = aiService.sendMessageStream(CHAT_REQUEST)
        chunks = list(generator)
        assert chunks == []


def test_sendMessageStream_exception():
    with patch('service.aiService.stream') as mock_stream:
        mock_stream.side_effect = Exception("Mocked exception")
        with pytest.raises(Exception) as ex_res:
            next(aiService.sendMessageStream(CHAT_REQUEST))
        assert str(ex_res.value) == aiService.ERROR_LANGCHAIN_SEND_CHAT_MESSAGE


def test_getMessages():
    with patch('service.aiService.get_session_history') as mock_history:
        msgs = [HumanMessage("question"), AIMessage("answer")]
        mock_history.return_value.messages = msgs
        messages = aiService.getMessages(USER)
        assert messages == [{'q': 'question'}, {'a': 'answer'}]
        mock_history.assert_called_once_with(USER)


def test_deleteMessages():
    with patch('service.aiService.delete_messages') as mock:
        aiService.deleteMessages(USER)
        mock.assert_called_once_with(USER)


def test_deleteMessages_w_index():
    with patch('service.aiService.delete_messages') as mock:
        aiService.deleteMessages(USER, 1)
        mock.assert_called_once_with(USER, [2, 2])
