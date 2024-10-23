from langchain_core.messages import AIMessageChunk
from model.model import ChatRequest
from service.langchain.langchainUtil import currentModel

USER = "testUser"
CHAT_REQUEST = ChatRequest(None, 'model', USER,
                           'question', 'history', 'ability')


def mockMsgFirstChunk() -> AIMessageChunk:
    return AIMessageChunk(content=f'testId#|S|E|P#{currentModel}#|S|E|P#ChatOpenAI#|S|E|P#', response_metadata={})


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
