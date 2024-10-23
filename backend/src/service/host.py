# Ollama default local host parameters
from langchain_ollama import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from util.logUtil import initLog

log = initLog(__file__)

supportedChatTypes = {'ollama': ChatOllama, 'openAI': ChatOpenAI}
selectedChatType = supportedChatTypes['openAI']

port = 11434
baseUrl = f"http://localhost:{port}"
hostArgsV1 = {"base_url": baseUrl + "/v1", "api_key": "xx"}
if selectedChatType == ChatOpenAI:
    baseUrl = baseUrl + "/v1"  # ChatOllama without uri /v1, ChatOpenAI with uri /v1
log.info(f"selectedChatType={selectedChatType}, baseUrl={baseUrl}")
hostArgs = {"base_url": baseUrl, "api_key": "xx", "verbose": True}
