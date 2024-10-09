from langchain_core.messages import AIMessageChunk
from model.model import ChatRequest


mock_chatReq = ChatRequest(None, 'model', 'user',
                           'question', 'history', 'ability')


def createMsgChunk(x):
    return AIMessageChunk(content=f"chunk{x}", response_metadata={"finish_reason": ""})


def generateMsgChunks():
    for x in range(1, 4):
        yield createMsgChunk(x)
