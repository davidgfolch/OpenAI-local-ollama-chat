import unittest
from unittest.mock import patch, MagicMock
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage
from common import USER, createMsgChunk, CHAT_REQUEST
from service.langchainUtil import CALLBACKS, currentModel, delete_messages, get_session_history, chatInstance, invoke, mapParams, stream, with_model, checkChunkError, store_folder


class TestLangchainUtil(unittest.TestCase):

    mock_history = MagicMock(spec=BaseChatMessageHistory)

    @patch('service.langchainUtil.FileChatMessageHistory')
    def test_get_session_history_new(self, mock_FileChatMessageHistory):
        mock_FileChatMessageHistory.return_value = self.mock_history
        history = get_session_history("testUserX")
        mock_FileChatMessageHistory.assert_called_once_with(
            file_path=f"{store_folder}testUserX.json", encoding="utf-8")
        self.assertEqual(history, self.mock_history)

    @patch('service.langchainUtil.store', new_callable=dict)
    @patch('service.langchainUtil.FileChatMessageHistory')
    def test_get_session_history_existing(self, mock_FileChatMessageHistory, mock_store):
        mock_store["existing_session"] = self.mock_history
        history = get_session_history("existing_session")
        mock_FileChatMessageHistory.assert_not_called()  # Shouldn't create new history
        self.assertEqual(history, self.mock_history)

    @patch('service.langchainUtil.ChatOpenAI')
    @patch('service.langchainUtil.hostArgs', new={})
    @patch('service.langchainUtil.ChatPromptTemplate')
    @patch('service.langchainUtil.RunnableWithMessageHistory')
    def test_chatInstance(self, mock_history, mock_ChatPromptTemplate, mock_ChatOpenAI):
        mock_llm = MagicMock()
        mock_ChatOpenAI.return_value = mock_llm
        mock_prompt = MagicMock()
        mock_ChatPromptTemplate.from_messages.return_value = mock_prompt
        chat_instance = chatInstance()
        mock_ChatOpenAI.assert_called_once_with(model=currentModel, **{})
        chain = mock_prompt | mock_llm
        chain = chain.with_config(callbacks=CALLBACKS)
        mock_history.assert_called_once_with(chain, get_session_history, input_messages_key="input", history_messages_key="history")
        self.assertEqual(chat_instance, mock_history.return_value)

    @patch('service.langchainUtil.with_model')
    def test_invoke(self, mock_model):
        mock_chat = MagicMock()
        mock_model.return_value = mock_chat
        result = invoke(CHAT_REQUEST)
        mock_model.assert_called_once_with(CHAT_REQUEST.model)
        mock_chat.invoke.assert_called_once_with(**mapParams(CHAT_REQUEST))
        self.assertEqual(result, mock_chat.invoke.return_value)

    @patch('service.langchainUtil.with_model')
    def test_stream(self, mock_model):
        mock_chat = MagicMock()
        mock_model.return_value = mock_chat
        result = stream(CHAT_REQUEST)
        mock_model.assert_called_once_with(CHAT_REQUEST.model)
        mock_chat.stream.assert_called_once_with(**mapParams(CHAT_REQUEST))
        self.assertEqual(result, mock_chat.stream.return_value)

    @patch('service.langchainUtil.FileChatMessageHistory')
    def test_delete_messages(self, mock_FileChatMessageHistory):
        self.mock_history.messages = [HumanMessage(content="Hi test!")]
        mock_FileChatMessageHistory.return_value = self.mock_history
        delete_messages(USER, [0])
        assert self.mock_history.messages == []
        mock_FileChatMessageHistory.assert_called_once_with(
            file_path=f"{store_folder}testUser.json", encoding="utf-8")
        delete_messages(USER, [0])
        delete_messages(USER)

    @patch('service.langchainUtil.chatInstance')
    def test_with_model_same(self, mock_chatInstance):
        with_model('')
        mock_chatInstance.assert_not_called()

    @patch('service.langchainUtil.chatInstance')
    def test_with_model_new(self, mock_chatInstance):
        mock_chat = MagicMock()
        mock_chatInstance.return_value = mock_chat
        result = with_model("new_model")
        mock_chatInstance.assert_called_once()
        self.assertEqual(result, mock_chat)

    def test_checkChunkError(self):
        try:
            checkChunkError(createMsgChunk(finish_reason='stop'))
        except Exception:
            self.fail("checkChunkError() raised Exception unexpectedly!")

    def test_checkChunkError_exception(self):
        with self.assertRaises(Exception) as context:
            checkChunkError(createMsgChunk(finish_reason='error'))
        self.assertEqual(str(context.exception),
                         "Error in stream chunk finish_reason is not stop")


if __name__ == '__main__':
    unittest.main()
