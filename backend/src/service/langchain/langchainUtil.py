import json
import re
from pathlib import Path
from typing import Callable, Dict, List, Set
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.base import RunnableBindingBase
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_ollama import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessageChunk, messages_to_dict

from model.model import ChatRequest
from service.host import hostArgs, DEFAULT_CHAT_TYPE
from service.langchain.files import processFiles
from service.langchain.model import UserData
from service.serviceException import ServiceException
from util.files import findFilesRecursive
from util.logUtil import initLog
from .callbackHandler import CallbackHandler
from .callbackHandlerAsync import CallbackHandlerAsync


log = initLog(__file__)

CALLBACKS = [CallbackHandler(), CallbackHandlerAsync()]
ERROR_STREAM_CHUNK = 'Error in stream chunk finish_reason is not stop, reason: '

# NOTE: ABILITY_FORMAT, if you change the format historyExport.py is affected (regular expressions)
ABILITY_FORMAT = """

IMPORTANTE:
- Antes de cada bloque de código generar un nombre de archivo con su extension.
- No repetir bloques de código, usar parametrización.

En el caso de generar bloques de de código las respuesta debe incluir un script de instalación para las librerias necesarias (sin comentarios añadidos, y sin nombre de archivo).
    - los bloques de código generados deben seguir las siguientes directrices:
        - incluir siempre el tipo de codigo generado sólo en la cabecera de codigo markdown.
        - evitar los comentarios evidentes, pero generando comentarios explicativos.
        - evitar saltos de linea innecesarios."""

DEFAULT_MODEL = "qwen2.5-coder:7b"  # llama3.2:latest  deepseek-coder-v2:16b
STORE_FOLDER = "./langchain.store/"
HISTORY_NAME_SEPARATOR = '_'
LAMBDA_PATH_TO_HISTORY_STR: Callable[[Path], str] = lambda p: p.name.split(HISTORY_NAME_SEPARATOR)[1].replace('.json', '')
STORE = {}


def getFilePath(session: str, extension='.json'):
    return f"{STORE_FOLDER}{session}{extension}"


def getSessionHistoryName(user: str, history: str) -> str:
    if len(user) == 0:
        raise ServiceException('User not specified')
    if len(history) == 0:
        raise ServiceException('History not specified')
    return user+HISTORY_NAME_SEPARATOR+history


def get_session_history(name: str) -> FileChatMessageHistory:
    log.debug(f'get_session_history name={name}')
    if name not in STORE:
        log.debug(f'new get_session_history for name={name}')
        if name.find(HISTORY_NAME_SEPARATOR) == -1:
            raise ServiceException(f'Invalid history name={name}')
        STORE[name] = FileChatMessageHistory(  # ChatMessageHistory()
            file_path=getFilePath(name), encoding="utf-8")
    return STORE[name]


def getUserHistories(user: str, sortFnc) -> List[Path]:
    files = findFilesRecursive(STORE_FOLDER, f'{user}_*.json')
    files.sort(key=lambda x: sortFnc(x))
    return list(map(LAMBDA_PATH_TO_HISTORY_STR, files))


def delete_messages(user: str, history: str, index: List[int] = None):
    session = getSessionHistoryName(user, history)
    if index:
        log.info(f"delete_messages pop index={index}")
        msgs = get_session_history(session).messages
        for i in index:
            try:
                msgs.pop(i)
            except IndexError:
                log.warning("Trying to delete non existent index")
        msgs = messages_to_dict(msgs)
        Path(getFilePath(session)).write_text(  # see implementation in langchain_community.chat_message_histories.file.FileChatMessageHistory
            json.dumps(msgs, ensure_ascii=True), encoding="utf-8")
        return
    get_session_history(session).clear()


def withModel(u: UserData) -> RunnableBindingBase:
    if u.model == '':
        u.model = DEFAULT_MODEL
    m = u.model.strip()
    if u.chatInstance and u.model == u.chatInstanceModel:
        log.info(f"Using same chat instance: '{DEFAULT_MODEL}'")
        return u.chatInstance
    log.info(f"New chat instance with model: {m}")
    u.model = m
    u.chatInstance = chatInstance(u)
    u.chatInstanceModel = m
    return u.chatInstance


def chatInstance(u: UserData) -> RunnableBindingBase:
    if u.chatType == ChatOllama:
        log.info(f"chatInstance ChatOllama with hostArgs={hostArgs}")
        llm = ChatOllama(model=u.model, temperature=u.temperature, **hostArgs)
    else:
        log.info(f"chatInstance ChatOpenAI with hostArgs={hostArgs}")
        llm = ChatOpenAI(model=u.model, temperature=u.temperature, **hostArgs)
    u.chatInstanceModel = u.model
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


FILES_REGEX = r'@/?(([a-zA-Z_-]+/)*[a-zA-Z_\-.0-9]+(\.[a-zA-Z]{1,3})?)'


def parseAndLoadQuestionFiles(question):
    all = re.findall(FILES_REGEX, question)
    files: Set[str] = set(map(lambda matchTuple: matchTuple[0], all))
    found: List[Document] = processFiles(files)
    input = re.sub(FILES_REGEX, r'\1', question)
    return input if len(found) == 0 else [input, found]


def mapUserData(r: ChatRequest):
    return UserData(user=r.user, model=r.model, temperature=r.temperature, ability=r.ability,
                    history=r.history, question=r.question, chatType=DEFAULT_CHAT_TYPE)


def mapParams(d: UserData) -> Dict:
    return {
        'input': {"history": getSessionHistoryName(d.user, d.history),
                  "ability": d.ability + ABILITY_FORMAT,
                  "input": parseAndLoadQuestionFiles(d.question)},
        'config': {
            "configurable": {
                "session_id": getSessionHistoryName(d.user, d.history),
                "model": d.model
            }
        }
    }


def invoke(d: UserData):
    return withModel(d).invoke(**mapParams(d))


def stream(d: UserData, params: Dict):
    first = True
    for chunk in withModel(d).stream(**params):
        if first:
            first = False
            yield generateFirstChunk(chunk.id, d)
        yield chunk
        last = generateLastChunk(chunk)
        if last:
            yield last
        log.debug(f"Received chunk={chunk}")
        checkChunkError(chunk)


def generateFirstChunk(chunkId: str, u: UserData):
    return AIMessageChunk(f'{chunkId}#|S|E|P#{u.model}#|S|E|P#{u.chatType.__name__}#|S|E|P#')


def generateLastChunk(chunk: AIMessageChunk):
    # https://python.langchain.com/docs/how_to/response_metadata/
    # OLlama {"model": "deepseek-coder-v2:16b", "created_at": "2024-10-23T09:47:01.306667386Z", "message": {"role": "assistant", "content": ""}, "done_reason": "stop", "done": true, "total_duration": 15846635838, "load_duration": 23860120, "prompt_eval_count": 267, "prompt_eval_duration": 5083022000, "eval_count": 79, "eval_duration": 10299011000}
    # OpenAI {'finish_reason': 'stop', 'model_name': 'deepseek-coder-v2:16b', 'system_fingerprint': 'fp_ollama'}
    if chunk.response_metadata:  # Only the last chunk comes with metadata
        return AIMessageChunk("#|S|E|P#" + json.dumps(chunk.response_metadata))


def checkChunkError(chunk: AIMessageChunk):
    """ Check finish_reason is ok"""
    reason = chunk.response_metadata.get('finish_reason', '')
    if (reason != '' and reason != 'stop'):
        raise Exception(f"{ERROR_STREAM_CHUNK}{reason}")
