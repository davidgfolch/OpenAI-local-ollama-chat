from host import hostArgs
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, BaseMessage #InMemoryChatMessageHistory,
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
# from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI
import json

from logConfig import initLog
from serviceException import ServiceException

store = {}

log = initLog(__file__)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(file_path="./langchain.store",encoding="utf-8") #ChatMessageHistory()
    return store[session_id]

model = ChatOpenAI(**hostArgs)
prompt = ChatPromptTemplate.from_messages([
        ("system","{ability}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
        ])
runnable = prompt | model

with_message_history = RunnableWithMessageHistory(runnable, get_session_history, input_messages_key="input", history_messages_key="history")

def ask(user: str, question:str, history = "history1", ability="Ingeniería de software"):
    log.info(f"asked to: {question}")
    try:
        res:AIMessage = with_message_history.invoke(
            input={"history": history, "ability": ability, "input": question},
            config={"configurable": {"session_id": user}})
    except Exception as e:
        raise RuntimeError(f'Error invoking openAI server: {hostArgs['base_url']}') from e
        # raise ServiceException('Error invoking openAI server: '+json.dumps(hostArgs), e)
    log.info(f"IA returns {res}")
    return res.content

def list(user: str): # todo parameterize ability, session_id, history
    log.info(f"User {user} list...")
    res = get_session_history(user)
    messages:list[BaseMessage]=res.messages
    log.info(f"IA returns messages {messages}")
    res = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            res.append({"q": msg.content})
        elif isinstance(msg, AIMessage):
            res.append({"a": msg.content})
    log.info(f"IA returns messages (mapped) {res}")
    return res

def delete(user: str):
    return get_session_history(user).clear()
