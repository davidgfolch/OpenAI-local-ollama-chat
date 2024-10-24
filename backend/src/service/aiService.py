import json
import logging
from langchain_core.chat_history import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk

from service.host import baseUrl, selectedChatType
from service.langchain.langchainUtil import checkChunkError, delete_messages, get_session_history, invoke, stream, currentModel
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


def sendMessageStream(r: ChatRequest):
    log.info(f"sendMessageStream to {r.model}: {r.question}")
    try:
        first = True
        for chunk in stream(r):
            if isCancelStreamSignal(r):
                break
            if first:
                first = False
                yield AIMessageChunk(
                    f"{chunk.id}#|S|E|P#{currentModel}#|S|E|P#{selectedChatType.__name__}#|S|E|P#")
            yield chunk
            # https://python.langchain.com/docs/how_to/response_metadata/
            # OLlama {"model": "deepseek-coder-v2:16b", "created_at": "2024-10-23T09:47:01.306667386Z", "message": {"role": "assistant", "content": ""}, "done_reason": "stop", "done": true, "total_duration": 15846635838, "load_duration": 23860120, "prompt_eval_count": 267, "prompt_eval_duration": 5083022000, "eval_count": 79, "eval_duration": 10299011000}
            # OpenAI {'finish_reason': 'stop', 'model_name': 'deepseek-coder-v2:16b', 'system_fingerprint': 'fp_ollama'}
            if chunk.response_metadata:  # Only the last chunk comes with metadata
                yield AIMessageChunk("#|S|E|P#" + json.dumps(chunk.response_metadata))
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
                        "metadata": '{"model": "' + msg.response_metadata.get('model_name','') + '"}',
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
