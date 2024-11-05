import copy
import logging
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.outputs.chat_generation import ChatGenerationChunk
from langchain_core.documents import Document

from util.truncateStrings import TruncateStrings
from util.logUtil import initLog

log = initLog(__file__, logging.INFO)


def truncate(o):
    return TruncateStrings({
        BaseMessage: ["content"],
        ChatPromptValue: ["messages"],
        LLMResult: ["generations"],
        ChatGenerationChunk: ["text", "message"],
        Document: ["page_content"]
    }).process(copy.deepcopy(o))


class CallbackHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized: dict[str, Any], messages: list[list[BaseMessage]], **kwargs) -> None:
        log.debug(f"on_chat_model_start ==> serialized={
                  truncate(serialized)}, messages={truncate(messages)}")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        log.debug(f"on_llm_end ==> response={truncate(response)}")

    def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs) -> None:
        log.debug(f"on_chain_start ==> serialized={
                  truncate(serialized)}, inputs={truncate(inputs)}")

    def on_chain_end(self, outputs: dict[str, Any], **kwargs) -> None:
        log.debug(f"on_chain_end ==> outputs={truncate(outputs)}")
