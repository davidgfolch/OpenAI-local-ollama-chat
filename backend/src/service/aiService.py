from langchain_core.chat_history import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage

from service.host import baseUrl
from service.langchainUtil import get_session_history, with_model
from model.model import ChatRequest
import service.openaiUtil as openaiUtil
from util.logUtil import initLog
from service.serviceException import ServiceException

log = initLog(__file__)

ERROR_OPENAI_GET_AVAILABLE_MODELS = f'Error invoking openAI server to get available models: {baseUrl}'
ERROR_LANGCHAIN_SEND_CHAT_MESSAGE = f'Error invoking/streaming openAI server: {baseUrl}'


def getModels() -> list:
    try:
        return openaiUtil.getModels()
    except Exception as e:
        raise ServiceException(ERROR_OPENAI_GET_AVAILABLE_MODELS) from e


def sendMessage(r: ChatRequest):
    log.info(f"invoke to {r.model}: {r.question}")
    try:
        res: AIMessage = with_model(r.model).invoke(
            input={"history": r.history,
                   "ability": r.ability, "input": r.question},
            config={"configurable": {"session_id": r.user, "model": r.model}})
    except Exception as e:
        raise ServiceException(ERROR_LANGCHAIN_SEND_CHAT_MESSAGE) from e
    log.info(f"IA returns {res}")
    return res.content


def sendMessageStream(r: ChatRequest):
    log.info(f"stream to {r.model}: {r.question}")
    try:
        call = with_model(r.model).stream(
            input={"history": r.history,
                   "ability": r.ability, "input": r.question},
            config={"configurable": {"session_id": r.user, "model": r.model}})
        for chunk in call:
            yield chunk
    except Exception as e:
        raise ServiceException(ERROR_LANGCHAIN_SEND_CHAT_MESSAGE) from e


def getMessages(user: str):  # TODO: parameterize session_id, history
    log.info(f"User {user} list...")
    res = get_session_history(user)
    messages: list[BaseMessage] = res.messages
    log.info(f"IA returns messages {messages}")
    res = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            res.append({"q": msg.content})
        elif isinstance(msg, AIMessage):
            res.append({"a": msg.content})
    log.info(f"IA returns messages (mapped) {res}")
    return res


def deleteMessages(user: str):
    return get_session_history(user).clear()