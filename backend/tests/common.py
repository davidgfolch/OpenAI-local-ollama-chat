from langchain_core.messages import AIMessageChunk
from model.model import ChatRequest
from service.langchain.langchainUtil import defaultModel, mapUserData

USER = "testUser"
CHAT_REQUEST = ChatRequest(defaultModel, USER, 'question', 'history', 'ability')
CHAT_REQUEST_NEW_MODEL = ChatRequest('testNewModel', USER, 'question', 'history', 'ability')
USER_DATA = mapUserData(CHAT_REQUEST)
USER_DATA_NEW_MODEL = mapUserData(CHAT_REQUEST_NEW_MODEL)


def mockMsgFirstChunk() -> AIMessageChunk:
    return AIMessageChunk(content=f'testId#|S|E|P#{defaultModel}#|S|E|P#ChatOpenAI#|S|E|P#', response_metadata={})


def mockMsgChunk(content='testContent', metadata=False, finishReason='') -> AIMessageChunk:
    resMetadata = {} if not metadata else {'finish_reason': finishReason,
                                           'model_name': 'testModel'}
    return AIMessageChunk(content=content,
                          response_metadata=resMetadata,
                          id='testId')


def mockMsgChunks(items: int, metadataChunk=False):
    for x in range(0, items):
        metadata = metadataChunk and x == items-1
        yield mockMsgChunk(content=f"chunk{x+1}", metadata=metadata)
