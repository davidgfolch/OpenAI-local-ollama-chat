import copy
import unittest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from service.serviceException import ServiceException
from tests.common import HISTORY, QUESTION, SESSION, TEMPERATURE, USER, USER_DATA, mockMsgChunk, CHAT_REQUEST
from service.langchain.langchainUtil import CALLBACKS, ERROR_STREAM_CHUNK, defaultModel, delete_messages, get_session_history, chatInstance, getFilePath, getSessionHistoryName, invoke, mapParams, parseAndLoadQuestionFiles, stream, withModel, checkChunkError
from langchain_community.chat_message_histories.file import FileChatMessageHistory


class TestLangchainUtil(unittest.TestCase):

    # mock_history = MagicMock(spec=BaseChatMessageHistory)
    mock_history = MagicMock(spec=FileChatMessageHistory)
    langchainUtil = "service.langchain.langchainUtil."

    @patch(f"{langchainUtil}FileChatMessageHistory")
    def test_get_session_history(self, MockFileChatMessageHistory):
        # Caso cuando el historial de sesión no está en el almacenamiento
        with patch.dict(f'{self.langchainUtil}store', {}, clear=True) as store:
            session_history = get_session_history(SESSION)
            self.assertIsInstance(session_history, MagicMock)
            self.assertIn(f"{USER}_{HISTORY}", store)
        # Caso cuando el historial de sesión ya está en el almacenamiento
        with patch.dict(f'{self.langchainUtil}store', {f"{USER}_{HISTORY}": "existing_history"}, clear=True):
            session_history = get_session_history(SESSION)
            self.assertEqual(session_history, "existing_history")

    @patch(langchainUtil+'ChatOpenAI')
    @patch(langchainUtil+'hostArgs', new={})
    @patch(langchainUtil+'ChatPromptTemplate')
    @patch(langchainUtil+'RunnableWithMessageHistory')
    def test_chatInstance(self, m_history, m_ChatPromptTemplate, mock_ChatOpenAI):
        mock_llm = MagicMock()
        mock_ChatOpenAI.return_value = mock_llm
        mock_prompt = MagicMock()
        m_ChatPromptTemplate.from_messages.return_value = mock_prompt
        chat_instance = chatInstance(USER_DATA)
        mock_ChatOpenAI.assert_called_once_with(
            model=defaultModel, temperature=TEMPERATURE, **{})
        chain = mock_prompt | mock_llm
        chain = chain.with_config(callbacks=CALLBACKS)
        m_history.assert_called_once_with(
            chain, get_session_history, input_messages_key="input", history_messages_key="history")
        self.assertEqual(chat_instance, m_history.return_value)
        # test chatType = ChatOllama
        USER_DATA.chatType = ChatOllama
        chat_instance = chatInstance(USER_DATA)
        self.assertEqual(chat_instance, m_history.return_value)

    @patch(langchainUtil+'withModel')
    def test_invoke(self, mock_model):
        mock_chat = MagicMock()
        mock_model.return_value = mock_chat
        result = invoke(CHAT_REQUEST)
        mock_model.assert_called_once_with(CHAT_REQUEST)
        mock_chat.invoke.assert_called_once_with(**mapParams(CHAT_REQUEST))
        self.assertEqual(result, mock_chat.invoke.return_value)

    @patch(langchainUtil+'withModel')
    def test_stream(self, mock_model):
        mock_chat = MagicMock()
        mock_model.return_value = mock_chat
        preParsedParams = mapParams(USER_DATA)
        result = stream(CHAT_REQUEST, preParsedParams)
        mock_model.assert_called_once_with(CHAT_REQUEST)
        mock_chat.stream.assert_called_once_with(**mapParams(CHAT_REQUEST))
        self.assertEqual(result, mock_chat.stream.return_value)

    @patch(langchainUtil+'FileChatMessageHistory')
    def test_delete_messages(self, m_history):
        self.mock_history.messages = [HumanMessage(content="Hi test!")]
        m_history.return_value = self.mock_history
        delete_messages(USER, HISTORY, [0])
        assert self.mock_history.messages == []
        m_history.assert_called_once_with(
            file_path=f"{getFilePath(SESSION)}", encoding="utf-8")
        delete_messages(USER, HISTORY, [0])
        delete_messages(USER, HISTORY)

    @patch(langchainUtil+'chatInstance')
    def test_withModel(self, mock_chatInstance):
        userData = copy.deepcopy(USER_DATA)
        userData.model = ''
        withModel(userData)
        mock_chatInstance.assert_called_once()
        assert userData.model == defaultModel
        withModel(userData)
        mock_chatInstance.assert_called_once()

    def test_checkChunkError(self):
        try:
            checkChunkError(mockMsgChunk(finishReason='stop'))
        except Exception:
            self.fail("checkChunkError() raised Exception unexpectedly!")

    def test_checkChunkError_exception(self):
        finishReason = 'error'
        with self.assertRaises(Exception) as context:
            mock = mockMsgChunk(metadata=True, finishReason=finishReason)
            checkChunkError(mock)
        self.assertEqual(str(context.exception),
                         ERROR_STREAM_CHUNK+finishReason)

    def test_parseAndLoadQuestionFiles(self):
        self.assertEqual(QUESTION, parseAndLoadQuestionFiles(QUESTION))

    def test_getSessionHistoryName(self):
        with self.assertRaises(ServiceException):
            getSessionHistoryName('', '')
        with self.assertRaises(ServiceException):
            getSessionHistoryName(USER, '')


if __name__ == '__main__':
    unittest.main()
