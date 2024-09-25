#from sqlalchemy import null
from host import hostArgs
from logConfig import console_handler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory, BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_openai.chat_models import ChatOpenAI
import logging

store = {}

logger = console_handler(logging.getLogger('iaServer'))

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

model = ChatOpenAI(**hostArgs)
prompt = ChatPromptTemplate.from_messages([
        ("system","Eres un asistente especializado en {ability}.  Puedes responder preguntas sobre {ability}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
        ])
runnable = prompt | model

with_message_history = RunnableWithMessageHistory(runnable, get_session_history, input_messages_key="input", history_messages_key="history")

def ask(user: str, question:str):
    logger.info(f"asked to: {question}")
    res:AIMessage = with_message_history.invoke(
        input={"history": "history1", "ability": "Ciencia de datos", "input": question},
        config={"configurable": {"session_id": "session_1"}})
    logger.info(f"IA returns {res}")
    return res.content

def list(user: str):
    logger.info(f"User {user} list...")
    res:InMemoryChatMessageHistory = get_session_history("session_1")
    messages:list[BaseMessage]=res.messages
    logger.info(f"IA returns messages {messages}")
    res = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            res.append({"q": msg.content})
        elif isinstance(msg, AIMessage):
            res.append({"a": msg.content})
    logger.info(f"IA returns messages (mapped) {res}")
    return res
    
#           CPU  GPU (GTX960M)
#tinyllama  ?:?? 2:56
#llama2     2:24 1:34 (llama2 with host model llama3.1)
#llama3.1   5:40 2:10