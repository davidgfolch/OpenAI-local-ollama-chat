from langchain_core.chat_history import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage

from host import hostArgs
from langchainUtil import get_session_history, with_model
import openaiUtil
from logConfig import initLog
from serviceException import ServiceException

log = initLog(__file__)

def getModels() -> list:
    try:
        return openaiUtil.getModels()
    except Exception as e:
        ex = ServiceException(f'Error invoking openAI server to get available models: {hostArgs['base_url']}')
        raise ex from e


def sendMessage(model: str, user: str, question: str, history="history1", ability="Ingeniería de software"):
    log.info(f"sendMessage to {model}: {question}")
    try:
        res: AIMessage = with_model(model).invoke(
            input={"history": history, "ability": ability, "input": question},
            config={"configurable": {"session_id": user, "model": model}})
    except Exception as e:
        ex = ServiceException(f'Error invoking openAI server: {hostArgs['base_url']}')
        raise ex from e
    log.info(f"IA returns {res}")
    return res.content


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
