import logging
from typing import Dict
from langchain_core.chat_history import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage

from service.host import baseUrl
from service.langchain.langchainUtil import checkChunkError, delete_messages, generateFirstChunk, generateLastChunk, get_session_history, mapParams, mapUserData, invoke, stream
from model.model import ChatRequest
import service.openaiUtil as openaiUtil
from util.logUtil import initLog
from service.serviceException import ServiceException

log = initLog(__file__, logging.INFO)

ERROR_OPENAI_GET_AVAILABLE_MODELS = f'Error invoking openAI server to get available models: {
    baseUrl}'
ERROR_LANGCHAIN_SEND_CHAT_MESSAGE = f'Error invoking/streaming openAI server: {
    baseUrl}'

cancelSignal = {}


def getModels() -> list:
    try:
        return openaiUtil.getModels()
    except Exception as e:
        raise ServiceException(ERROR_OPENAI_GET_AVAILABLE_MODELS) from e


def sendMessage(r: ChatRequest):  # NOT USED
    log.info(f"invoke to {r.model}: {r.question}")
    try:
        res = invoke(r)
    except Exception as e:
        raise ServiceException(ERROR_LANGCHAIN_SEND_CHAT_MESSAGE) from e
    log.info(f"IA returns {res}")
    return res.content


def cancelStreamSignal(user):
    global cancelSignal
    cancelSignal.update({user: True})


def isCancelStreamSignal(r: ChatRequest):
    global cancelSignal
    if cancelSignal.get(r.user, None):
        cancelSignal.update({r.user: False})
        return True
    return False


def preParseParams(r: ChatRequest):
    userData = mapUserData(r)
    return mapParams(userData)


def sendMessageStream(req: ChatRequest, preParsedParams: Dict):
    log.info(f"sendMessageStream to {req.model}: {req.question}")
    try:
        first = True
        userData = mapUserData(req)
        for chunk in stream(userData, preParsedParams):
            if isCancelStreamSignal(req):
                break
            if first:
                first = False
                yield generateFirstChunk(chunk.id, userData)
            yield chunk
            last = generateLastChunk(chunk)
            if last:
                yield last
            log.debug(f"Received chunk={chunk}")
            checkChunkError(chunk)
    except Exception as e:
        raise ServiceException(ERROR_LANGCHAIN_SEND_CHAT_MESSAGE) from e


def getMessages(user: str):  # TODO: parameterize session_id, history
    log.info(f"User {user} list...")
    res = get_session_history(user)
    messages: list[BaseMessage] = res.messages
    log.debug(f"IA returns messages {messages}")
    res = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            res.append({"q": msg.content})
        elif isinstance(msg, AIMessage):
            res.append({"a": msg.content,
                        "metadata": '{"model": "' + msg.response_metadata.get('model_name', '') + '"}',
                        "id": msg.id})
    log.debug(f"IA returns messages (mapped) {res}")
    return res


def deleteMessages(user: str, index: int = None):
    if index is not None:
        log.info(f"deleteMessages user={user} index={index*2}")
        delete_messages(user, [index*2, index*2])
        return
    log.info(f"deleteMessages user={user}")
    delete_messages(user)
