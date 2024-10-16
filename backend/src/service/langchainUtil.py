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


log = initLog(__file__)
store = {}
currentModel = "deepseek-coder-v2:16b"


def getFilePath(session_id: str):
    return f"./langchain.store/{session_id}.json"


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
                log.warning("Trying to delete nonexisten index")
        msgs = messages_to_dict(msgs)
        Path(getFilePath(user)).write_text(
            # see implementation in langchain_community.chat_message_histories.file.FileChatMessageHistory
            json.dumps(msgs, ensure_ascii=True), encoding="utf-8"
        )
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
