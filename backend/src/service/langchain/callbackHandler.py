import logging
from typing import Any, Dict
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.outputs.chat_generation import ChatGenerationChunk

from service.langchain.truncateStrings import truncateStrings, setTruncateAttrMap
from util.logUtil import initLog

log = initLog(__file__, logging.DEBUG)

def setTruncateLangchainClasses():
    setTruncateAttrMap({
        BaseMessage: ["content"],
        ChatPromptValue: ["messages"],
        LLMResult: ["generations"],
        ChatGenerationChunk: ["text", "message"]
    })


class CallbackHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized: dict[str, Any], messages: list[list[BaseMessage]], **kwargs) -> None:
        log.debug(f"on_chat_model_start ==> serialized={truncateStrings(serialized)}, messages={truncateStrings(messages)}")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        log.debug(f"on_llm_end ==> response={truncateStrings(response)}")

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        log.debug(f"on_chain_start ==> serialized={truncateStrings(serialized)}, inputs={truncateStrings(inputs)}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        log.debug(f"on_chain_end ==> outputs={truncateStrings(outputs)}")
