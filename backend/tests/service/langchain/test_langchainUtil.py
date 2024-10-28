import copy
import unittest
from unittest.mock import patch, MagicMock
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from tests.common import USER, USER_DATA, mockMsgChunk, CHAT_REQUEST
from service.langchain.langchainUtil import CALLBACKS, ERROR_STREAM_CHUNK, defaultModel, delete_messages, get_session_history, chatInstance, invoke, mapParams, stream, withModel, checkChunkError, store_folder


class TestLangchainUtil(unittest.TestCase):

    mock_history = MagicMock(spec=BaseChatMessageHistory)
    langchainUtil = "service.langchain.langchainUtil."

    @patch(langchainUtil+'FileChatMessageHistory')
    def test_get_session_history_new(self, m_history):
        m_history.return_value = self.mock_history
        history = get_session_history("testUserX")
        m_history.assert_called_once_with(
            file_path=f"{store_folder}testUserX.json", encoding="utf-8")
        self.assertEqual(history, self.mock_history)

    @patch(langchainUtil+'store', new_callable=dict)
    @patch(langchainUtil+'FileChatMessageHistory')
    def test_get_session_history_existing(self, m_history, m_store):
        m_store["existing_session"] = self.mock_history
        history = get_session_history("existing_session")
        m_history.assert_not_called()  # Shouldn't create new history
        self.assertEqual(history, self.mock_history)

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
        mock_ChatOpenAI.assert_called_once_with(model=defaultModel, **{})
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
        delete_messages(USER, [0])
        assert self.mock_history.messages == []
        m_history.assert_called_once_with(
            file_path=f"{store_folder}testUser.json", encoding="utf-8")
        delete_messages(USER, [0])
        delete_messages(USER)

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


if __name__ == '__main__':
    unittest.main()
