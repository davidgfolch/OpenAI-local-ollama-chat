from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# InMemoryChatMessageHistory,
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI

from host import hostArgs
from logConfig import initLog


log = initLog(__file__)
store = {}
# "llama3.1-claude" "mistral"  "llama3.1:8b"
currentModel = "deepseek-coder-v2:16b"

# TODO: checkout automatic model selection, but it will make the response slower: https://github.com/PromptEngineer48/LLM_Selector/blob/main/main_working.py

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(
            # ChatMessageHistory()
            file_path="./langchain.store", encoding="utf-8")
    return store[session_id]


def chatInstance():
    llm = ChatOpenAI(model=currentModel, **hostArgs)
    # llm = ChatOllama(model=currentModel, verbose=True) #https://python.langchain.com/docs/integrations/chat/ollama/
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{ability}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    runnable = prompt | llm
    return RunnableWithMessageHistory(runnable, get_session_history,
                                      input_messages_key="input",
                                      history_messages_key="history")


# TODO: streaming https://python.langchain.com/docs/how_to/structured_output/#streaming
# asyncCallbackHandler = AsyncCallbackHandler()
# model = ChatOpenAI(streaming=True, callbacks=asyncCallbackHandler**hostArgs)


def with_model(model: str):
    global currentModel, chat
    m = model.strip()
    if model == '' or currentModel == m:
        log.info("Same model!")
        return chat
    log.info(f"New chatInscance with model: {m}")
    currentModel = m
    chat = chatInstance()
    return chat


chat = chatInstance()
