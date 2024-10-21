import json
from pathlib import Path
from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessageChunk, messages_to_dict

from model.model import ChatRequest
from service.host import hostArgs
from util.logUtil import initLog
from .callbackHandler import CallbackHandler
from .callbackHandlerAsync import CallbackHandlerAsync


log = initLog(__file__)

CALLBACKS = [CallbackHandler(), CallbackHandlerAsync()]
store_folder = "./langchain.store/"
store = {}
currentModel = "deepseek-coder-v2:16b"


def getFilePath(session_id: str):
    return f"{store_folder}{session_id}.json"


def get_session_history(user: str) -> FileChatMessageHistory:
    if user not in store:
        store[user] = FileChatMessageHistory(  # ChatMessageHistory()
            file_path=getFilePath(user), encoding="utf-8")
    return store[user]


def delete_messages(user: str, index: List[int] = None):
    if index:
        log.info(f"delete_messages pop index={index}")
        msgs = get_session_history(user).messages
        for i in index:
            try:
                msgs.pop(i)
            except IndexError:
                log.warning("Trying to delete non existent index")
        msgs = messages_to_dict(msgs)
        Path(getFilePath(user)).write_text(  # see implementation in langchain_community.chat_message_histories.file.FileChatMessageHistory
            json.dumps(msgs, ensure_ascii=True), encoding="utf-8")
        return
    get_session_history(user).clear()


def with_model(model: str):
    global currentModel, chat
    m = model.strip()
    if model == '' or currentModel == m:
        log.info(f"Using same model: '{currentModel}'")
        return chat
    log.info(f"New chat instance with model: {m}")
    currentModel = m
    return chatInstance()


def chatInstance():
    llm = ChatOpenAI(model=currentModel, **hostArgs)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{ability}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    chain = prompt | llm
    chain = chain.with_config(callbacks=CALLBACKS)
    return RunnableWithMessageHistory(chain, get_session_history,
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
