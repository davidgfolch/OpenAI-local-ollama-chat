from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessageChunk

from model.model import ChatRequest
from service.host import hostArgs
from util.logUtil import initLog


log = initLog(__file__)
store = {}
currentModel = "deepseek-coder-v2:16b"


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(
            # ChatMessageHistory()
            file_path="./langchain.store", encoding="utf-8")
    return store[session_id]


def with_model(model: str):
    global currentModel, chat
    m = model.strip()
    if model == '' or currentModel == m:
        log.info(f"Using same model: '{currentModel}'")
        return chat
    log.info(f"New chat instance with model: {m}")
    currentModel = m
    chat = chatInstance()
    return chat


def chatInstance():
    llm = ChatOpenAI(model=currentModel, **hostArgs)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{ability}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    runnable = prompt | llm
    return RunnableWithMessageHistory(runnable, get_session_history,
                                      input_messages_key="input",
                                      history_messages_key="history")


def mapParams(r: ChatRequest):
    return {'input': {"history": r.history, "ability": r.ability, "input": r.question},
            'config': {"configurable": {"session_id": r.user, "model": r.model}}}


def invoke(r: ChatRequest):
    return with_model(r.model).invoke(**mapParams(r))


def stream(r: ChatRequest):
    return with_model(r.model).stream(**mapParams(r))


def checkChunkError(chunk: AIMessageChunk):
    """ Check finish_reason is ok"""
    reason = chunk.response_metadata.get('finish_reason', '')
    if (reason != '' and reason != 'stop'):
        raise Exception("Error in stream chunk finish_reason is not stop")


chat = chatInstance()
