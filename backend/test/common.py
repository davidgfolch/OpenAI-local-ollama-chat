from langchain_core.messages import AIMessageChunk
from model.model import ChatRequest

USER = "testUser"
CHAT_REQUEST = ChatRequest(None, 'model', USER,
                           'question', 'history', 'ability')


def createMsgChunk(content='xx', finish_reason='') -> AIMessageChunk:
    return AIMessageChunk(content=content, response_metadata={"finish_reason": finish_reason})


def generateMsgChunks():
    for x in range(1, 4):
        yield createMsgChunk(content=f"chunk{x}")
