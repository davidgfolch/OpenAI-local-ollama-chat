# Ollama default local host parameters
from langchain_ollama import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from util.logUtil import initLog

log = initLog(__file__)

SUPPORTED_CHAT_TYPES = {'ollama': ChatOllama, 'openAI': ChatOpenAI}
DEFAULT_CHAT_TYPE = SUPPORTED_CHAT_TYPES['openAI']

port = 11434
baseUrl = f"http://localhost:{port}"
hostArgsV1 = {"base_url": baseUrl + "/v1", "api_key": "xx"}
if DEFAULT_CHAT_TYPE == ChatOpenAI:
    baseUrl = baseUrl + "/v1"  # ChatOllama without uri /v1, ChatOpenAI with uri /v1
log.info(f"selectedChatType={DEFAULT_CHAT_TYPE}, baseUrl={baseUrl}")
hostArgs = {"base_url": baseUrl, "api_key": "xx", "verbose": True}
