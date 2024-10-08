import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk
from model.model import ChatRequest
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

mock_req = ChatRequest(None, 'model', 'user', 'question', 'history', 'ability')


def test_sendMessage():
    with patch('service.aiService.invoke') as mock_invoke:
        mock_res = MagicMock()
        mock_res.content = "testResponse"
        mock_invoke.return_value = mock_res
        res = aiService.sendMessage(mock_req)
        assert res == "testResponse"
        mock_invoke.assert_called_once_with(mock_req)


def test_sendMessage_exception():
    with patch('service.aiService.invoke') as mock_invoke:
        mock_invoke.side_effect = Exception("Mocked exception")
        with pytest.raises(Exception) as ex_res:
            aiService.sendMessage(mock_req)
        assert str(ex_res.value) == aiService.ERROR_LANGCHAIN_SEND_CHAT_MESSAGE

def createChunk(x):
    return AIMessageChunk(content=f"chunk1{x}", response_metadata={"finish_reason": ""})


def test_sendMessageStream():
    def generatorResp():
        for x in range(1, 4):
            yield createChunk(x)
    with patch('service.aiService.stream') as mock_stream:
        mock_stream.return_value = generatorResp()
        generator = aiService.sendMessageStream(mock_req)
        chunks = list(generator)
        print(f"chunks={chunks}")
        for x in range(1, 4):
            assert chunks[x-1] == createChunk(x)


# def test_sendMessageStream_exception():
#     with patch('service.aiService.stream') as mock_stream:
#         mock_stream.side_effect = Exception("Mocked exception")
#         with pytest.raises(Exception) as ex_res:
#             aiService.sendMessageStream(mock_req)
#         assert str(ex_res.value) == aiService.ERROR_LANGCHAIN_SEND_CHAT_MESSAGE
    # with patch('service.aiService.with_model') as mock_with_model:
    #     mock_with_model.side_effect = Exception("Mocked exception")
    #     try:
    #         aiService.sendMessageStream(ChatRequest(None, '', '', '', '', ''))
    #     except Exception as ex:
    #         assert str(ex) == aiService.ERROR_LANGCHAIN_SEND_CHAT_MESSAGE


def test_getMessages():
    with patch('service.aiService.get_session_history') as mock_get_session_history:
        msgs = [HumanMessage("question"), AIMessage("answer")]
        mock_get_session_history.return_value.messages = msgs
        messages = aiService.getMessages('testUser')
        assert messages == [{'q': 'question'}, {'a': 'answer'}]
        mock_get_session_history.assert_called_once_with('testUser')


def test_deleteMessages():
    with patch('service.aiService.get_session_history') as mock_get_session_history:
        mock_get_session_history().clear = MagicMock()
        aiService.deleteMessages('testUser')
        mock_get_session_history.return_value.clear.assert_called_once()
